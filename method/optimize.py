#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cma
import numpy as np
import torch

from data.glider_proxy import base_shape_library, hydrodynamic_coefficients, lift_to_drag, write_design
from method.model import FluidSurrogate


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/fluid_surrogate.pt")
    parser.add_argument("--output-dir", default="outputs/proposed")
    parser.add_argument("--angles", default="9,30")
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--population", type=int, default=24)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    bases, names = base_shape_library()
    model = FluidSurrogate(input_dim=bases.shape[1] + 1)
    ckpt = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_results = []

    for angle in [float(v) for v in args.angles.split(",") if v.strip()]:
        x0 = np.zeros(len(bases), dtype=np.float64)
        sigma0 = 0.85
        es = cma.CMAEvolutionStrategy(
            x0,
            sigma0,
            {
                "seed": args.seed + int(angle * 10),
                "popsize": args.population,
                "maxiter": args.generations,
                "verb_disp": 0,
                "verbose": -9,
            },
        )

        def objective(z: np.ndarray) -> float:
            weights = softmax(z)
            shape = weights @ bases
            features = np.concatenate([shape, [angle / 30.0]], dtype=np.float32)
            with torch.no_grad():
                pred = model(torch.tensor(features[None, :], dtype=torch.float32))[0].numpy()
            cd, cl = float(pred[0]), float(pred[1])
            return -lift_to_drag(cd, cl)

        while not es.stop():
            solutions = es.ask()
            scores = [objective(np.asarray(s)) for s in solutions]
            es.tell(solutions, scores)

        weights = softmax(np.asarray(es.result.xbest))
        shape = weights @ bases
        with torch.no_grad():
            pred = model(torch.tensor(np.concatenate([shape, [angle / 30.0]], dtype=np.float32)[None, :]))[0].numpy()
        pred_eta = lift_to_drag(float(pred[0]), float(pred[1]))
        cd, cl = hydrodynamic_coefficients(shape, angle)
        oracle_eta = lift_to_drag(float(cd), float(cl))
        top_components = sorted(zip(names, weights.tolist()), key=lambda item: item[1], reverse=True)[:5]
        result = {
            "angle": angle,
            "shape": shape.astype(float).tolist(),
            "weights": weights.astype(float).tolist(),
            "top_base_components": top_components,
            "surrogate_cd": float(pred[0]),
            "surrogate_cl": float(pred[1]),
            "surrogate_lift_to_drag": pred_eta,
            "oracle_cd": float(cd),
            "oracle_cl": float(cl),
            "oracle_lift_to_drag": oracle_eta,
            "surrogate_eta_abs_pct_error": abs(pred_eta - oracle_eta) / max(oracle_eta, 1e-8) * 100.0,
        }
        all_results.append(result)

    best = max(all_results, key=lambda item: item["oracle_lift_to_drag"])
    write_design(
        output_dir / "optimization_results.json",
        "ai_enhanced_glider",
        np.array(best["shape"], dtype=np.float32),
        float(best["angle"]),
        {
            "selection": "best_cma_es_design_across_requested_angles",
            "all_angle_results": all_results,
            "surrogate_lift_to_drag": best["surrogate_lift_to_drag"],
            "surrogate_eta_abs_pct_error": best["surrogate_eta_abs_pct_error"],
        },
    )
    (output_dir / "all_results.json").write_text(json.dumps(all_results, indent=2) + "\n")


if __name__ == "__main__":
    main()
