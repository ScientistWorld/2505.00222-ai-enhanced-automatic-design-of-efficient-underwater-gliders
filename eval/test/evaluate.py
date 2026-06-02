#!/usr/bin/env python3
"""Held-out test-slice evaluator for glider design artifacts.

This evaluator reads the same method artifacts as the train slice, then
rescored them on held-out operating conditions. It intentionally avoids
dependencies on method code or eval/train code.
"""

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


POOL_ANGLES_DEG = (12.0, 24.0)
ANGLE_SWEEP_LABELS = (9, 30)
ANGLE_SWEEP_EVAL_ANGLES = {9: 12.0, 30: 24.0}
SURROGATE_VALIDATION_LABEL = 30
BASE_SHAPES, _BASE_NAMES = base_shape_library()
FEATURE_MIN = BASE_SHAPES.min(axis=0)
FEATURE_MAX = BASE_SHAPES.max(axis=0)


def load_design(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing design artifact: {path}")
    return json.loads(path.read_text())


def load_optional_design(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    return load_design(path)


def is_baseline_design(path: Path, design: dict) -> bool:
    name = str(design.get("name", path.parent.name)).lower()
    return name in {"torpedo", "torpedo_baseline"} or path.parent.name.lower() in {
        "torpedo",
        "torpedo_baseline",
    }


def discover_artifacts(outputs_dir: Path) -> tuple[Path | None, list[Path]]:
    baseline = None
    proposed = []
    for path in sorted(outputs_dir.glob("*/optimization_results.json")):
        try:
            design = load_design(path)
        except (OSError, json.JSONDecodeError):
            continue
        if is_baseline_design(path, design):
            baseline = path
        else:
            proposed.append(path)
    return baseline, proposed


def train_result_keys(path: Path = Path("scoring/scores_train.json")) -> dict[str, set[str]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    experiments = data.get("experiments", data)
    keys = {}
    for exp_name, exp_data in experiments.items():
        if exp_name.startswith("_") or not isinstance(exp_data, dict):
            continue
        results = exp_data.get("results", exp_data)
        if isinstance(results, dict):
            keys[exp_name] = {key for key in results if not key.startswith("_")}
    return keys


def result_name(path: Path, design: dict, baseline: bool = False) -> str:
    name = str(design.get("name") or path.parent.name)
    if baseline and name.lower() == "torpedo":
        return "torpedo_baseline"
    return name


def angle_result_prefix(method_name: str) -> str:
    if method_name.endswith("_glider"):
        return method_name[: -len("_glider")]
    return method_name


def shape_metrics(shape: np.ndarray, angles: tuple[float, ...]) -> dict:
    etas = []
    energies = []
    trajectories = []
    for angle in angles:
        cd, cl = hydrodynamic_coefficients(shape, angle)
        eta = lift_to_drag(float(cd), float(cl))
        etas.append(eta)
        energies.append(float(1.0 / max(eta, 1e-8)))
        trajectories.append(trajectory_angle_deg(eta))
    return {
        "lift_to_drag": float(np.mean(etas)),
        "energy_per_distance_relative": float(np.mean(energies)),
        "trajectory_angle_deg": float(np.mean(trajectories)),
        "cage_feature_range_violation": cage_feature_range_violation(shape),
    }


def cage_feature_range_violation(shape: np.ndarray) -> float:
    """Mean absolute excursion outside the base-shape feature envelope."""

    below = np.maximum(FEATURE_MIN - shape, 0.0)
    above = np.maximum(shape - FEATURE_MAX, 0.0)
    return float(np.mean(below + above))


def with_gain(metrics: dict, baseline_eta: float) -> dict:
    out = dict(metrics)
    out["efficiency_gain_over_torpedo"] = float(
        metrics["lift_to_drag"] / max(baseline_eta, 1e-8)
    )
    return out


def find_angle_record(design: dict, label: int) -> dict | None:
    records = design.get("all_angle_results") or []
    if not records:
        return None
    return min(records, key=lambda item: abs(float(item.get("angle", label)) - label))


def metrics_for_angle_record(design: dict, label: int, eval_angle: float, baseline_eta: float) -> dict:
    record = find_angle_record(design, label)
    shape = np.asarray((record or design)["shape"], dtype=np.float32)
    return with_gain(shape_metrics(shape, (eval_angle,)), baseline_eta)


def surrogate_metrics(design: dict, label: int) -> dict:
    record = find_angle_record(design, label) or design
    angle = float(record.get("angle", record.get("aoa_deg", label)))
    shape = np.asarray(record["shape"], dtype=np.float32)
    oracle = shape_metrics(shape, (angle,))
    oracle_eta = oracle["lift_to_drag"]
    if "surrogate_lift_to_drag" in record:
        surrogate_eta = float(record["surrogate_lift_to_drag"])
    elif "surrogate_cd" in record and "surrogate_cl" in record:
        surrogate_eta = lift_to_drag(float(record["surrogate_cd"]), float(record["surrogate_cl"]))
    else:
        surrogate_eta = float(design.get("surrogate_lift_to_drag", oracle_eta))
    error = abs(surrogate_eta - oracle_eta) / max(abs(oracle_eta), 1e-8) * 100.0
    return {
        "lift_to_drag": oracle_eta,
        "surrogate_lift_to_drag": surrogate_eta,
        "surrogate_eta_abs_pct_error": float(error),
        "raw_lift_to_drag": oracle_eta,
        "raw_surrogate_lift_to_drag": surrogate_eta,
    }


def assert_covers_train_keys(scores: dict, expected: dict[str, set[str]]) -> None:
    if not expected:
        return
    experiments = scores.get("experiments", {})
    missing = {}
    for exp_name, train_keys in expected.items():
        if exp_name not in experiments:
            missing[exp_name] = sorted(train_keys)
            continue
        test_keys = set(experiments[exp_name].get("results", {}))
        gap = sorted(train_keys - test_keys)
        if gap:
            missing[exp_name] = gap
    if missing:
        raise RuntimeError(
            "Test slice did not score every method key present in "
            f"scoring/scores_train.json: {missing}"
        )


def build_scores(baseline_path: Path, proposed_paths: list[Path]) -> dict:
    baseline = load_design(baseline_path)
    baseline_shape = np.asarray(baseline["shape"], dtype=np.float32)
    baseline_metrics = shape_metrics(baseline_shape, POOL_ANGLES_DEG)
    baseline_eta = baseline_metrics["lift_to_drag"]
    angle_baseline_eta = {
        label: shape_metrics(baseline_shape, (eval_angle,))["lift_to_drag"]
        for label, eval_angle in ANGLE_SWEEP_EVAL_ANGLES.items()
    }
    pool_results = {
        result_name(baseline_path, baseline, baseline=True): with_gain(
            baseline_metrics, baseline_eta
        )
    }

    angle_results = {}
    surrogate_results = {}
    for path in proposed_paths:
        design = load_design(path)
        method_name = result_name(path, design)
        shape = np.asarray(design["shape"], dtype=np.float32)
        pool_results[method_name] = with_gain(
            shape_metrics(shape, POOL_ANGLES_DEG), baseline_eta
        )

        prefix = angle_result_prefix(method_name)
        for label in ANGLE_SWEEP_LABELS:
            angle_results[f"{prefix}_{label}deg"] = metrics_for_angle_record(
                design, label, ANGLE_SWEEP_EVAL_ANGLES[label], angle_baseline_eta[label]
            )

        surrogate_results[method_name] = surrogate_metrics(
            design, SURROGATE_VALIDATION_LABEL
        )

    scores = {
        "_slice": "test",
        "experiments": {
            "pool_efficiency": {"results": pool_results},
        },
    }
    if angle_results:
        scores["experiments"]["angle_sweep_efficiency"] = {"results": angle_results}
    if surrogate_results:
        scores["experiments"]["surrogate_validation"] = {"results": surrogate_results}
    return scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposed", default=None)
    parser.add_argument("--baseline", default=None)
    parser.add_argument("--output", default="scoring/scores_test.json")
    parser.add_argument("--outputs-dir", default="outputs")
    args = parser.parse_args()

    discovered_baseline, discovered_proposed = discover_artifacts(Path(args.outputs_dir))
    baseline_path = Path(args.baseline) if args.baseline else discovered_baseline
    if baseline_path is None:
        baseline_path = Path(args.outputs_dir) / "torpedo" / "optimization_results.json"

    if args.proposed:
        proposed_paths = [Path(args.proposed)] if Path(args.proposed).exists() else []
    else:
        proposed_paths = discovered_proposed

    if not baseline_path.exists() and proposed_paths:
        raise FileNotFoundError(
            "Proposed designs require a baseline artifact so "
            "`efficiency_gain_over_torpedo` can be computed."
        )
    if not baseline_path.exists():
        raise FileNotFoundError(f"Missing baseline design artifact: {baseline_path}")

    scores = build_scores(baseline_path, proposed_paths)
    assert_covers_train_keys(scores, train_result_keys())
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
