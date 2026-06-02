#!/usr/bin/env python3
"""Evaluate design artifacts without importing method code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from data.glider_proxy import hydrodynamic_coefficients, lift_to_drag, trajectory_angle_deg


def load_design(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing design artifact: {path}")
    return json.loads(path.read_text())


def metrics_for_design(design: dict) -> dict:
    shape = np.asarray(design["shape"], dtype=np.float32)
    angle = float(design["aoa_deg"])
    cd, cl = hydrodynamic_coefficients(shape, angle)
    eta = lift_to_drag(float(cd), float(cl))
    return {
        "lift_to_drag": eta,
        "energy_per_distance_relative": float(1.0 / max(eta, 1e-8)),
        "trajectory_angle_deg": trajectory_angle_deg(eta),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposed", default="outputs/proposed/optimization_results.json")
    parser.add_argument("--baseline", default="outputs/torpedo/optimization_results.json")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    proposed = load_design(Path(args.proposed))
    baseline = load_design(Path(args.baseline))
    proposed_metrics = metrics_for_design(proposed)
    baseline_metrics = metrics_for_design(baseline)

    surrogate_error = float(proposed.get("surrogate_eta_abs_pct_error", 0.0))
    if "surrogate_lift_to_drag" in proposed:
        surrogate_eta = float(proposed["surrogate_lift_to_drag"])
    else:
        surrogate_eta = proposed_metrics["lift_to_drag"]

    scores = {
        "experiments": {
            "pool_efficiency": {
                "results": {
                    "torpedo_baseline": baseline_metrics,
                    "ai_enhanced_glider": proposed_metrics,
                }
            },
            "surrogate_validation": {
                "results": {
                    "ai_enhanced_glider": {
                        "lift_to_drag": proposed_metrics["lift_to_drag"],
                        "surrogate_lift_to_drag": surrogate_eta,
                        "surrogate_eta_abs_pct_error": surrogate_error,
                    }
                }
            },
        }
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
