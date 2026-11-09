#!/usr/bin/env python3
"""End-to-end AI-enhanced glider design for every published fluid instance.

Per instance: train the neural fluid surrogate on the instance's labelled
dataset, run convex-hull-constrained CMA-ES at every angle on the design grid,
co-design (shape, angle) by surrogate efficiency, and predict coefficients for
the instance's query inputs. Writes ``<output-dir>/optimization_results.json``.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from data.glider_proxy import DESIGN_ANGLES, all_instance_ids, instance_design, load_queries, write_artifact
from method.optimize import design_instance
from method.train_surrogate import Predictor, features, train_surrogate


def parse_angles(text: str) -> list[float]:
    return [float(v) for v in text.split(",") if v.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/proposed")
    parser.add_argument("--name", default="ai_enhanced_glider")
    parser.add_argument("--instances", default="all", help="'all' or a comma-separated list of instance ids")
    parser.add_argument("--checkpoint-dir", default="checkpoints")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--ensemble", type=int, default=1, help="number of independently seeded surrogates averaged")
    parser.add_argument("--target-transform", default="log_cd", choices=["log_cd", "standard"])
    parser.add_argument("--schedule", default="constant", choices=["constant", "cosine"])
    parser.add_argument("--angles", default="0,3,6,9,12,15,18,21,24,27,30")
    parser.add_argument("--restarts", type=int, default=3)
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--population", type=int, default=24)
    args = parser.parse_args()

    ids = all_instance_ids() if args.instances == "all" else [v for v in args.instances.split(",") if v]
    angles = parse_angles(args.angles)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    instances, info = {}, {}
    for iid in ids:
        t0 = time.time()
        ckpts = [
            train_surrogate(iid, args.epochs, args.lr, args.batch_size, args.warmup,
                            seed=args.seed * 1000 + k, log_every=0,
                            target_transform=args.target_transform, schedule=args.schedule)
            for k in range(args.ensemble)
        ]
        if args.checkpoint_dir:
            Path(args.checkpoint_dir).mkdir(parents=True, exist_ok=True)
            torch.save(ckpts, Path(args.checkpoint_dir) / f"{args.name}_{iid}.pt")
        predictor = Predictor(ckpts)
        t1 = time.time()
        design = design_instance(predictor, angles, list(DESIGN_ANGLES), args.restarts,
                                 args.generations, args.population, args.seed)
        queries = load_queries(iid)
        preds = predictor.coefficients(features(queries["shape"], queries["aoa_deg"]))
        preds[:, 0] = np.maximum(preds[:, 0], 1e-6)
        instances[iid] = instance_design(design["pool_weights"], design["pool_aoa_deg"],
                                         design["angle_weights"], preds)
        info[iid] = {
            "pool_aoa_deg": design["pool_aoa_deg"],
            "surrogate_predicted_eta": design["predicted_eta"],
            "best_val_mse": [c["best_val_mse"] for c in ckpts],
            "best_epoch": [c["best_epoch"] for c in ckpts],
            "final_val_eta_mape_percent": [c["history"][-1]["val_eta_mape_percent"] for c in ckpts],
            "train_seconds": t1 - t0,
            "search_seconds": time.time() - t1,
        }
        print(json.dumps({"instance": iid, **info[iid]}), flush=True)
    write_artifact(out_dir / "optimization_results.json", args.name, instances,
                   {"method_info": {"settings": vars(args), "instances": info}})
    (out_dir / "surrogate_training.json").write_text(json.dumps(info, indent=2) + "\n")


if __name__ == "__main__":
    main()
