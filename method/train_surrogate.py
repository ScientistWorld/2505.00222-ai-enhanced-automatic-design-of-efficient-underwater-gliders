#!/usr/bin/env python3
"""Neural fluid surrogate: (hull descriptors, angle of attack) -> (c_d, c_l).

Paper settings: 4-layer MLP with batch normalisation and tanh, MSE loss, Adam
with learning rate 0.1, batch size 128, a 10-epoch warm-up and 200 epochs,
trained on every labelled hull (base shapes + 10 morphs per pair) at five
angles of attack between -30 and +30 degrees.

Target preprocessing (not specified by the paper): the network regresses the
standardised log drag coefficient and the standardised lift coefficient
(``target_transform="log_cd"``), so drag is learned to relative accuracy at
every angle; ``"standard"`` (standardised raw coefficients) is kept for
comparison. ``schedule="cosine"`` (decay after warm-up) is an optional variant;
the paper's schedule is warm-up then constant learning rate.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from data.glider_proxy import load_labels
from method.model import FluidSurrogate

torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "1")))


def features(shape: np.ndarray, aoa_deg: np.ndarray) -> np.ndarray:
    shape = np.atleast_2d(np.asarray(shape, dtype=np.float32))
    aoa = np.broadcast_to(np.asarray(aoa_deg, dtype=np.float32), (shape.shape[0],))
    return np.concatenate([shape, (aoa / 30.0)[:, None]], axis=1).astype(np.float32)


def train_surrogate(
    instance_id: str,
    epochs: int = 200,
    lr: float = 0.1,
    batch_size: int = 128,
    warmup: int = 10,
    seed: int = 0,
    log_every: int = 50,
    target_transform: str = "log_cd",
    schedule: str = "constant",
) -> dict:
    """Train one surrogate on an instance's labelled dataset; return a checkpoint dict."""

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    labels = load_labels(instance_id)
    x = features(labels["shape"], labels["aoa_deg"])
    y = np.stack([labels["cd"], labels["cl"]], axis=1).astype(np.float32)
    y_model = encode_targets(y, target_transform)
    n = len(x)
    order = rng.permutation(n)
    split = int(0.8 * n)
    train_idx, val_idx = order[:split], order[split:]
    y_mean = y_model[train_idx].mean(axis=0)
    y_std = np.maximum(y_model[train_idx].std(axis=0), 1e-6)
    y_scaled = (y_model - y_mean) / y_std

    loader = DataLoader(
        TensorDataset(torch.tensor(x[train_idx]), torch.tensor(y_scaled[train_idx])),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    val_x = torch.tensor(x[val_idx])
    val_y = torch.tensor(y[val_idx])
    val_y_scaled = torch.tensor(y_scaled[val_idx])
    mean_t, std_t = torch.tensor(y_mean), torch.tensor(y_std)

    model = FluidSurrogate(input_dim=x.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()
    history, best_val, best_state, best_epoch = [], float("inf"), None, 0
    for epoch in range(epochs):
        model.train()
        scale = min(1.0, (epoch + 1) / float(max(warmup, 1)))
        if schedule == "cosine" and epoch >= warmup:
            scale = 0.5 * (1.0 + np.cos(np.pi * (epoch - warmup) / max(epochs - warmup, 1)))
        for group in opt.param_groups:
            group["lr"] = lr * scale
        losses = []
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach()))
        model.eval()
        with torch.no_grad():
            pred_scaled = model(val_x)
            val_loss = float(loss_fn(pred_scaled, val_y_scaled))
            pred = torch.tensor(decode_targets((pred_scaled * std_t + mean_t).numpy(), target_transform)).clamp_min(1e-6)
            eta_p = pred[:, 1] / pred[:, 0]
            eta_t = val_y[:, 1] / val_y[:, 0].clamp_min(1e-8)
            mask = eta_t > 0.5
            mape = float((torch.abs(eta_p - eta_t)[mask] / eta_t[mask]).mean() * 100.0) if mask.any() else float("nan")
        history.append({"epoch": epoch + 1, "train_mse": float(np.mean(losses)), "val_mse": val_loss,
                        "val_eta_mape_percent": mape})
        if np.isfinite(val_loss) and val_loss < best_val:
            best_val, best_epoch = val_loss, epoch + 1
            best_state = copy.deepcopy(model.state_dict())
        if log_every and ((epoch + 1) % log_every == 0 or epoch == 0):
            print(json.dumps({"instance": instance_id, "seed": seed, **history[-1]}), flush=True)
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return {
        "state_dict": model.state_dict(),
        "input_dim": int(x.shape[1]),
        "target_mean": y_mean.tolist(),
        "target_std": y_std.tolist(),
        "target_transform": target_transform,
        "schedule": schedule,
        "best_epoch": best_epoch,
        "best_val_mse": best_val,
        "history": history,
        "seed": seed,
        "instance": instance_id,
    }


def encode_targets(y: np.ndarray, transform: str) -> np.ndarray:
    """(c_d, c_l) -> network targets before standardisation."""

    if transform == "log_cd":
        return np.stack([np.log(np.maximum(y[:, 0], 1e-6)), y[:, 1]], axis=1).astype(np.float32)
    if transform == "standard":
        return y.astype(np.float32)
    raise ValueError(f"unknown target transform {transform!r}")


def decode_targets(t: np.ndarray, transform: str) -> np.ndarray:
    if transform == "log_cd":
        return np.stack([np.exp(np.clip(t[:, 0], -30.0, 30.0)), t[:, 1]], axis=1)
    return np.asarray(t)


def load_model(ckpt: dict) -> FluidSurrogate:
    model = FluidSurrogate(input_dim=ckpt["input_dim"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model


class Predictor:
    """Mean prediction of one or more trained surrogates, in coefficient units."""

    def __init__(self, ckpts: list[dict]):
        self.models = [load_model(c) for c in ckpts]
        self.means = [np.asarray(c["target_mean"], dtype=np.float32) for c in ckpts]
        self.stds = [np.asarray(c["target_std"], dtype=np.float32) for c in ckpts]
        self.transforms = [c.get("target_transform", "standard") for c in ckpts]

    def coefficients(self, x: np.ndarray) -> np.ndarray:
        xt = torch.tensor(np.asarray(x, dtype=np.float32))
        outs = []
        with torch.no_grad():
            for m, mu, sd, tr in zip(self.models, self.means, self.stds, self.transforms):
                outs.append(decode_targets(m(xt).numpy() * sd + mu, tr))
        return np.mean(outs, axis=0)

    def lift_to_drag(self, x: np.ndarray) -> np.ndarray:
        pred = np.maximum(self.coefficients(x), 1e-6)
        return pred[:, 1] / pred[:, 0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--target-transform", default="log_cd", choices=["log_cd", "standard"])
    parser.add_argument("--schedule", default="constant", choices=["constant", "cosine"])
    args = parser.parse_args()
    ckpt = train_surrogate(args.instance, args.epochs, args.lr, args.batch_size, args.warmup, args.seed,
                           target_transform=args.target_transform, schedule=args.schedule)
    Path(args.checkpoint).parent.mkdir(parents=True, exist_ok=True)
    torch.save(ckpt, args.checkpoint)


if __name__ == "__main__":
    main()
