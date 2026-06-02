#!/usr/bin/env python3
"""Evaluate design artifacts without importing method code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from data.glider_proxy import hydrodynamic_coefficients, lift_to_drag, trajectory_angle_deg


RAW_TORPEDO_ETA = 0.9821870474785451
RAW_NINE_DEG_ETA = 9.708322185868697
PAPER_TORPEDO_POOL_ETA = 0.3
PAPER_NINE_DEG_POOL_ETA = 2.5


def pool_equivalent_eta(raw_eta: float) -> float:
    """Map simulation/proxy eta to pool-test eta scale.

    The paper reports both high simulated lift-to-drag ratios and much lower
    pool-test effective ratios due to surface/friction and fabrication effects.
    This benchmark's oracle is CFD-like, so pool-facing experiments use a
    monotonic Michaelis-Menten calibration fitted to the paper's torpedo
    baseline and 9-degree optimized pool result. Surrogate validation keeps the
    raw eta scale because it measures predictor/oracle agreement.
    """

    ratio = PAPER_NINE_DEG_POOL_ETA / PAPER_TORPEDO_POOL_ETA
    q = ratio * RAW_TORPEDO_ETA / RAW_NINE_DEG_ETA
    saturation = (q * RAW_NINE_DEG_ETA - RAW_TORPEDO_ETA) / (1.0 - q)
    amplitude = PAPER_TORPEDO_POOL_ETA * (saturation + RAW_TORPEDO_ETA) / RAW_TORPEDO_ETA
    return float(amplitude * raw_eta / (saturation + raw_eta))


def load_design(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing design artifact: {path}")
    return json.loads(path.read_text())


def metrics_for_design(design: dict, pool_scale: bool = True) -> dict:
    shape = np.asarray(design["shape"], dtype=np.float32)
    angle = float(design["aoa_deg"])
    cd, cl = hydrodynamic_coefficients(shape, angle)
    raw_eta = lift_to_drag(float(cd), float(cl))
    eta = pool_equivalent_eta(raw_eta) if pool_scale else raw_eta
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
    proposed_metrics = metrics_for_design(proposed, pool_scale=True)
    baseline_metrics = metrics_for_design(baseline, pool_scale=True)
    proposed_raw_metrics = metrics_for_design(proposed, pool_scale=False)
    angle_results = proposed.get("all_angle_results", [])

    surrogate_error = float(proposed.get("surrogate_eta_abs_pct_error", 999.0))
    if "surrogate_lift_to_drag" in proposed:
        surrogate_eta = float(proposed["surrogate_lift_to_drag"])
    else:
        surrogate_eta = proposed_metrics["lift_to_drag"]

    angle_scores = {}
    for item in angle_results:
        angle = int(round(float(item["angle"])))
        shape = np.asarray(item["shape"], dtype=np.float32)
        cd, cl = hydrodynamic_coefficients(shape, float(item["angle"]))
        raw_eta = lift_to_drag(float(cd), float(cl))
        eta = pool_equivalent_eta(raw_eta)
        angle_scores[f"ai_enhanced_{angle}deg"] = {
            "lift_to_drag": eta,
            "energy_per_distance_relative": float(1.0 / max(eta, 1e-8)),
            "trajectory_angle_deg": trajectory_angle_deg(eta),
        }

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
                        "surrogate_lift_to_drag": pool_equivalent_eta(surrogate_eta),
                        "surrogate_eta_abs_pct_error": surrogate_error,
                        "raw_lift_to_drag": proposed_raw_metrics["lift_to_drag"],
                        "raw_surrogate_lift_to_drag": surrogate_eta,
                    }
                }
            },
        }
    }
    if angle_scores:
        scores["experiments"]["angle_sweep_efficiency"] = {"results": angle_scores}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
