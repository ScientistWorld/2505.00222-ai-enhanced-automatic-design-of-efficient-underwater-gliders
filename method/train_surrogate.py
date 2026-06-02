#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from data.glider_proxy import sample_training_table
from method.model import FluidSurrogate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/fluid_surrogate.pt")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--morphs-per-pair", type=int, default=3)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    x, y = sample_training_table(args.morphs_per_pair)
    n = len(x)
    order = np.random.permutation(n)
    split = int(0.8 * n)
    train_idx, val_idx = order[:split], order[split:]
    y_mean = y[train_idx].mean(axis=0).astype(np.float32)
    y_std = y[train_idx].std(axis=0).astype(np.float32)
    y_std = np.maximum(y_std, 1e-6)
    y_scaled = (y - y_mean) / y_std
    train = TensorDataset(torch.tensor(x[train_idx]), torch.tensor(y_scaled[train_idx]))
    val_x = torch.tensor(x[val_idx])
    val_y = torch.tensor(y[val_idx])
    val_y_scaled = torch.tensor(y_scaled[val_idx])

    loader = DataLoader(train, batch_size=args.batch_size, shuffle=True)
    model = FluidSurrogate(input_dim=x.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = torch.nn.MSELoss()
    history = []
    best_val_loss = float("inf")
    best_state = None
    best_epoch = 0

    for epoch in range(args.epochs):
        model.train()
        # Linear warm-up for the first 10 epochs, as in the paper.
        scale = min(1.0, (epoch + 1) / 10.0)
        for group in opt.param_groups:
            group["lr"] = args.lr * scale
        losses = []
        for xb, yb in loader:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach()))
        model.eval()
        with torch.no_grad():
            val_pred_scaled = model(val_x)
            val_loss = float(loss_fn(val_pred_scaled, val_y_scaled))
            y_mean_t = torch.tensor(y_mean)
            y_std_t = torch.tensor(y_std)
            val_pred = val_pred_scaled * y_std_t + y_mean_t
            val_pred = val_pred.clamp_min(1e-6)
            eta_pred = val_pred[:, 1] / val_pred[:, 0].clamp_min(1e-8)
            eta_true = val_y[:, 1] / val_y[:, 0].clamp_min(1e-8)
            eta_mape = float((torch.abs(eta_pred - eta_true) / eta_true.clamp_min(1e-4)).mean() * 100.0)
        history.append({"epoch": epoch + 1, "train_mse": float(np.mean(losses)), "val_mse": val_loss, "eta_mape_percent": eta_mape})
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch + 1
            best_state = copy.deepcopy(model.state_dict())
        if (epoch + 1) % 25 == 0 or epoch == 0:
            print(json.dumps(history[-1]), flush=True)

    out = Path(args.checkpoint)
    out.parent.mkdir(parents=True, exist_ok=True)
    if best_state is not None:
        model.load_state_dict(best_state)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "history": history,
            "best_epoch": best_epoch,
            "best_val_mse": best_val_loss,
            "input_dim": x.shape[1],
            "target_mean": y_mean.tolist(),
            "target_std": y_std.tolist(),
        },
        out,
    )
    Path("outputs/proposed").mkdir(parents=True, exist_ok=True)
    Path("outputs/proposed/surrogate_training.json").write_text(json.dumps({"history": history}, indent=2) + "\n")


if __name__ == "__main__":
    main()
