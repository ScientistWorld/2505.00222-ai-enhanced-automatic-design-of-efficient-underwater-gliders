#!/usr/bin/env python3
"""Evaluate design artifacts without importing method code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from data.glider_proxy import (
    base_shape_library,
    hydrodynamic_coefficients,
    lift_to_drag,
    trajectory_angle_deg,
)


BASE_SHAPES, _BASE_NAMES = base_shape_library()
FEATURE_MIN = BASE_SHAPES.min(axis=0)
FEATURE_MAX = BASE_SHAPES.max(axis=0)


def load_design(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing design artifact: {path}")
    return json.loads(path.read_text())


def load_optional_design(path: Path) -> dict | None:
    if not path.exists():
        return None
    return load_design(path)


def metrics_for_design(design: dict) -> dict:
    shape = np.asarray(design["shape"], dtype=np.float32)
    angle = float(design["aoa_deg"])
    cd, cl = hydrodynamic_coefficients(shape, angle)
    eta = lift_to_drag(float(cd), float(cl))
    return {
        "lift_to_drag": eta,
        "energy_per_distance_relative": float(1.0 / max(eta, 1e-8)),
        "trajectory_angle_deg": trajectory_angle_deg(eta),
        "shape_domain_violation": shape_domain_violation(shape),
    }


def shape_domain_violation(shape: np.ndarray) -> float:
    below = np.maximum(FEATURE_MIN - shape, 0.0)
    above = np.maximum(shape - FEATURE_MAX, 0.0)
    return float(np.mean(below + above))


def with_gain(metrics: dict, baseline_eta: float) -> dict:
    out = dict(metrics)
    out["efficiency_gain_over_torpedo"] = float(metrics["lift_to_drag"] / max(baseline_eta, 1e-8))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposed", default="outputs/proposed/optimization_results.json")
    parser.add_argument("--baseline", default="outputs/torpedo/optimization_results.json")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    proposed = load_optional_design(Path(args.proposed))
    baseline = load_optional_design(Path(args.baseline))
    if proposed is None and baseline is None:
        raise FileNotFoundError(
            "No design artifacts found. Expected at least one of "
            f"{args.proposed!r} or {args.baseline!r}."
        )

    if proposed is not None and baseline is None:
        raise FileNotFoundError(
            "Proposed designs require a baseline artifact so "
            "`efficiency_gain_over_torpedo` can be computed. Run "
            "`bash scripts/baseline.sh` first or provide --baseline."
        )

    baseline_metrics = metrics_for_design(baseline) if baseline is not None else None
    proposed_metrics = metrics_for_design(proposed) if proposed is not None else None
    baseline_eta = baseline_metrics["lift_to_drag"]
    baseline_metrics = with_gain(baseline_metrics, baseline_eta)
    if proposed_metrics is not None:
        proposed_metrics = with_gain(proposed_metrics, baseline_eta)
    angle_results = proposed.get("all_angle_results", []) if proposed is not None else []

    angle_scores = {}
    for item in angle_results:
        angle = int(round(float(item["angle"])))
        shape = np.asarray(item["shape"], dtype=np.float32)
        cd, cl = hydrodynamic_coefficients(shape, float(item["angle"]))
        eta = lift_to_drag(float(cd), float(cl))
        angle_scores[f"ai_enhanced_{angle}deg"] = with_gain({
            "lift_to_drag": eta,
            "energy_per_distance_relative": float(1.0 / max(eta, 1e-8)),
            "trajectory_angle_deg": trajectory_angle_deg(eta),
            "shape_domain_violation": shape_domain_violation(shape),
        }, baseline_eta)

    pool_results = {"torpedo_baseline": baseline_metrics}
    if proposed_metrics is not None:
        pool_results["ai_enhanced_glider"] = proposed_metrics

    scores = {"experiments": {"pool_efficiency": {"results": pool_results}}}
    if proposed is not None:
        surrogate_error = float(proposed.get("surrogate_eta_abs_pct_error", 999.0))
        if "surrogate_lift_to_drag" in proposed:
            surrogate_eta = float(proposed["surrogate_lift_to_drag"])
        else:
            surrogate_eta = proposed_metrics["lift_to_drag"]
        scores["diagnostics"] = {
            "surrogate_validation": {
                "results": {
                    "ai_enhanced_glider": {
                        "lift_to_drag": proposed_metrics["lift_to_drag"],
                        "surrogate_lift_to_drag": surrogate_eta,
                        "surrogate_eta_abs_pct_error": surrogate_error,
                        "raw_lift_to_drag": proposed_metrics["lift_to_drag"],
                        "raw_surrogate_lift_to_drag": surrogate_eta,
                    }
                }
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
