#!/usr/bin/env python3
"""Development-slice evaluator for glider design artifacts.

Scores every ``outputs/<method>/optimization_results.json`` on the public
development fluid instances. Everything on the comparison side is fixed here:
the hydrodynamic ground truth, the torpedo baseline and its operating point,
the instance list, the design angles, the query set and the angle range.
Only raw method outputs are read (convex weights over the base hulls, angles of
attack and predicted coefficients); every scored number is recomputed.

Artifact schema (per method)::

    {"name": "<method>_glider",
     "instances": {"<instance id>": {
         "pool_design": {"weights": [20 floats], "aoa_deg": float},
         "angle_designs": {"9": {"weights": [...]}, "30": {"weights": [...]}},
         "query_predictions": [[c_d, c_l], ...]}}}

A malformed or physically impossible value anywhere (non-finite numbers,
weights outside the simplex, an angle outside the actuator range, a
non-positive predicted drag) fails the whole run: every scored metric of every
experiment then takes its worst value. A missing design or prediction scores
the worst value for that item.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from eval.train import hydro as H

SLICE = "train"
INSTANCES = {"dev_0": "dev-0", "dev_1": "dev-1"}
DESIGN_ANGLES = ("9", "30")
TORPEDO_AOA_GRID = [-30.0 + 0.25 * i for i in range(241)]
ETA_FLOOR = 0.01
WEIGHT_SUM_TOL = 1e-4
WEIGHT_NEG_TOL = 1e-6
EFFICIENCY_METRICS = (
    "efficiency_gain_over_torpedo",
    "lift_to_drag",
    "energy_per_distance_relative",
    "trajectory_angle_deg",
)
WORST = {
    "efficiency_gain_over_torpedo": 0.0,
    "lift_to_drag": 0.0,
    "energy_per_distance_relative": 1.0 / ETA_FLOOR,
    "trajectory_angle_deg": 90.0,
    "surrogate_eta_abs_pct_error": 100.0,
}
RESERVED = {"torpedo", "torpedo_baseline"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class InvalidSubmission(ValueError):
    pass


def _number(value, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidSubmission(f"{where}: expected a number, got {type(value).__name__}")
    v = float(value)
    if not math.isfinite(v):
        raise InvalidSubmission(f"{where}: non-finite value {value!r}")
    return v


def parse_weights(obj, where: str) -> list[float]:
    if not isinstance(obj, list) or len(obj) != H.NB:
        raise InvalidSubmission(f"{where}: weights must be a list of {H.NB} numbers")
    w = [_number(v, f"{where}[{i}]") for i, v in enumerate(obj)]
    if min(w) < -WEIGHT_NEG_TOL:
        raise InvalidSubmission(f"{where}: negative convex weight {min(w)!r} (outside the hull)")
    total = sum(w)
    if abs(total - 1.0) > WEIGHT_SUM_TOL:
        raise InvalidSubmission(f"{where}: weights sum to {total!r}, not 1 (outside the hull)")
    w = [max(v, 0.0) for v in w]
    total = sum(w)
    return [v / total for v in w]


def parse_aoa(value, where: str) -> float:
    a = _number(value, where)
    lo, hi = H.AOA_RANGE_DEG
    if a < lo - 1e-9 or a > hi + 1e-9:
        raise InvalidSubmission(f"{where}: angle of attack {a} outside [{lo}, {hi}] degrees")
    return a


def efficiency(eta: float, torpedo_eta: float) -> dict:
    e = max(float(eta), 0.0)
    return {
        "efficiency_gain_over_torpedo": e / torpedo_eta,
        "lift_to_drag": e,
        "energy_per_distance_relative": 1.0 / max(e, ETA_FLOOR),
        "trajectory_angle_deg": math.degrees(math.atan2(1.0, e)),
    }


def worst_efficiency() -> dict:
    return {m: WORST[m] for m in EFFICIENCY_METRICS}


def mean_rows(rows: list[dict]) -> dict:
    keys = rows[0].keys()
    return {k: float(sum(r[k] for r in rows) / len(rows)) for k in keys}


def instance_context(instance_id: str, seed: str) -> dict:
    inst = H.make_instance(seed)
    torpedo = H.BASE_SHAPES[H.TORPEDO_INDEX]
    best_eta, best_aoa = max((H.lift_to_drag(inst, torpedo, a), a) for a in TORPEDO_AOA_GRID)
    angle_eta = {lab: H.lift_to_drag(inst, torpedo, float(lab)) for lab in DESIGN_ANGLES}
    queries = H.query_inputs(instance_id)
    truth = [H.coefficients(inst, q["shape"], q["aoa_deg"]) for q in queries]
    return {
        "instance": inst, "torpedo_eta": best_eta, "torpedo_aoa": best_aoa,
        "torpedo_angle_eta": angle_eta, "queries": queries, "truth": truth,
    }


def score_instance(design, ctx: dict, where: str) -> dict:
    """Return per-instance raw results; raises InvalidSubmission on impossible values."""

    inst = ctx["instance"]
    out = {"pool": None, "angles": {lab: None for lab in DESIGN_ANGLES}, "query_error": None}
    if design is None:
        return out
    if not isinstance(design, dict):
        raise InvalidSubmission(f"{where}: instance entry must be an object")

    pool = design.get("pool_design")
    if pool is not None:
        if not isinstance(pool, dict):
            raise InvalidSubmission(f"{where}.pool_design: must be an object")
        w = parse_weights(pool.get("weights"), f"{where}.pool_design.weights")
        aoa = parse_aoa(pool.get("aoa_deg"), f"{where}.pool_design.aoa_deg")
        out["pool"] = {"eta": H.lift_to_drag(inst, H.mix(w), aoa), "aoa_deg": aoa}

    angles = design.get("angle_designs")
    if angles is not None:
        if not isinstance(angles, dict):
            raise InvalidSubmission(f"{where}.angle_designs: must be an object")
        for lab in DESIGN_ANGLES:
            item = angles.get(lab)
            if item is None:
                continue
            if not isinstance(item, dict):
                raise InvalidSubmission(f"{where}.angle_designs.{lab}: must be an object")
            w = parse_weights(item.get("weights"), f"{where}.angle_designs.{lab}.weights")
            out["angles"][lab] = H.lift_to_drag(inst, H.mix(w), float(lab))

    preds = design.get("query_predictions")
    if preds is not None:
        n = len(ctx["queries"])
        if not isinstance(preds, list) or len(preds) != n:
            raise InvalidSubmission(f"{where}.query_predictions: expected a list of {n} [c_d, c_l] pairs")
        errors = []
        for i, (pair, (cd_t, cl_t)) in enumerate(zip(preds, ctx["truth"])):
            if not isinstance(pair, list) or len(pair) != 2:
                raise InvalidSubmission(f"{where}.query_predictions[{i}]: expected [c_d, c_l]")
            cd = _number(pair[0], f"{where}.query_predictions[{i}][0]")
            cl = _number(pair[1], f"{where}.query_predictions[{i}][1]")
            if cd <= 0.0:
                raise InvalidSubmission(f"{where}.query_predictions[{i}]: drag coefficient must be positive")
            eta_p = max(cl, 0.0) / cd
            eta_t = cl_t / cd_t
            errors.append(min(abs(eta_p - eta_t) / max(eta_t, 1.0) * 100.0, 100.0))
        out["query_error"] = float(sum(errors) / len(errors))
    return out


def score_method(artifact, contexts: dict) -> tuple[dict, list[str]]:
    """Return (per-instance raw results, failure reasons)."""

    if not isinstance(artifact, dict):
        return {}, ["artifact is not a JSON object"]
    instances = artifact.get("instances")
    if not isinstance(instances, dict):
        return {}, ["artifact has no 'instances' object"]
    raw = {}
    try:
        for iid, ctx in contexts.items():
            raw[iid] = score_instance(instances.get(iid), ctx, f"instances.{iid}")
    except InvalidSubmission as exc:
        return {}, [str(exc)]
    return raw, []


def aggregate(raw: dict, contexts: dict, failed: bool) -> dict:
    pool_rows, angle_rows, query_rows = [], {lab: [] for lab in DESIGN_ANGLES}, []
    for iid, ctx in contexts.items():
        r = raw.get(iid) if not failed else None
        pool = r["pool"] if r else None
        pool_rows.append(efficiency(pool["eta"], ctx["torpedo_eta"]) if pool else worst_efficiency())
        for lab in DESIGN_ANGLES:
            eta = r["angles"][lab] if r else None
            angle_rows[lab].append(
                efficiency(eta, ctx["torpedo_angle_eta"][lab]) if eta is not None else worst_efficiency()
            )
        q = r["query_error"] if r else None
        query_rows.append({"surrogate_eta_abs_pct_error": q if q is not None else WORST["surrogate_eta_abs_pct_error"]})
    return {
        "pool": mean_rows(pool_rows),
        "angles": {lab: mean_rows(rows) for lab, rows in angle_rows.items()},
        "surrogate": mean_rows(query_rows),
    }


def canonical_names() -> list[str]:
    try:
        ref = json.loads(Path("scoring/reference.json").read_text())
        rows = ref["experiments"]["pool_efficiency"]["results"]
        names = [k for k, v in rows.items() if isinstance(v, dict) and v.get("type") == "proposed"]
        if names:
            return names
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return ["ai_enhanced_glider"]


def discover(outputs_dir: Path) -> list[tuple[str, object]]:
    """Return [(result key, artifact or None)] for every method artifact on disk."""

    found = []
    for path in sorted(outputs_dir.glob("*/optimization_results.json")):
        try:
            artifact = json.loads(path.read_text())
        except (OSError, ValueError):
            artifact = None
        name = artifact.get("name") if isinstance(artifact, dict) else None
        valid = isinstance(name, str) and bool(NAME_RE.match(name)) and name.lower() not in RESERVED
        found.append((path.parent.name, artifact, name if valid else None))
    if not found:
        # Nothing submitted: the canonical rows still exist, at their worst values.
        return [(c, None) for c in canonical_names()]
    used: set[str] = set()
    keys: list[str | None] = [None] * len(found)
    # Valid self-declared names first, so a broken artifact never takes a valid method's key.
    for i, (_, _, name) in enumerate(found):
        if name and name not in used:
            keys[i] = name
            used.add(name)
    canonical = canonical_names()
    for i, (dirname, _, _) in enumerate(found):
        if keys[i] is not None:
            continue
        base = next((c for c in canonical if c not in used), f"{dirname}_glider")
        key, n = base, 2
        while key in used:
            key, n = f"{base}_{n}", n + 1
        keys[i] = key
        used.add(key)
    return [(key, artifact) for key, (_, artifact, _) in zip(keys, found)]


def angle_prefix(key: str) -> str:
    return key[: -len("_glider")] if key.endswith("_glider") else key


def build_scores(outputs_dir: Path) -> dict:
    contexts = {iid: instance_context(iid, seed) for iid, seed in INSTANCES.items()}
    torpedo_rows = [efficiency(ctx["torpedo_eta"], ctx["torpedo_eta"]) for ctx in contexts.values()]
    pool_results = {"torpedo_baseline": mean_rows(torpedo_rows)}
    angle_results, surrogate_results, validity, per_instance = {}, {}, {}, {}
    for key, artifact in discover(outputs_dir):
        if artifact is None:
            raw, reasons = {}, ["missing or unreadable optimization_results.json"]
        else:
            raw, reasons = score_method(artifact, contexts)
        failed = bool(reasons)
        agg = aggregate(raw, contexts, failed)
        pool_results[key] = agg["pool"]
        prefix = angle_prefix(key)
        for lab in DESIGN_ANGLES:
            angle_results[f"{prefix}_{lab}deg"] = agg["angles"][lab]
        surrogate_results[key] = agg["surrogate"]
        validity[key] = {"failed": failed, "reasons": reasons}
        per_instance[key] = {
            iid: {
                "pool_eta": (r["pool"] or {}).get("eta"),
                "pool_aoa_deg": (r["pool"] or {}).get("aoa_deg"),
                **{f"eta_{lab}deg": r["angles"][lab] for lab in DESIGN_ANGLES},
                "query_eta_abs_pct_error": r["query_error"],
            }
            for iid, r in raw.items()
        }
    return {
        "_slice": SLICE,
        "experiments": {
            "pool_efficiency": {"results": pool_results},
            "angle_sweep_efficiency": {"results": angle_results},
            "surrogate_validation": {"results": surrogate_results},
        },
        "diagnostics": {
            "validity": validity,
            "instances": {
                iid: {"torpedo_best_eta": ctx["torpedo_eta"], "torpedo_best_aoa_deg": ctx["torpedo_aoa"],
                      **{f"torpedo_eta_{lab}deg": v for lab, v in ctx["torpedo_angle_eta"].items()}}
                for iid, ctx in contexts.items()
            },
            "per_instance": per_instance,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", default="outputs")
    parser.add_argument("--output", default="scoring/scores_train.json")
    args = parser.parse_args()
    scores = build_scores(Path(args.outputs_dir))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores["experiments"], indent=2))
    for key, v in scores["diagnostics"]["validity"].items():
        if v["failed"]:
            print(f"[{SLICE}] {key}: FAILED -> worst values ({'; '.join(v['reasons'])})")


if __name__ == "__main__":
    main()
