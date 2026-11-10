# Evaluation Protocol

## Submission

Write one artifact per method to `outputs/<method>/optimization_results.json`:

```json
{
  "name": "ai_enhanced_glider",
  "instances": {
    "<instance id>": {
      "pool_design":   {"weights": [20 numbers], "aoa_deg": 12.0},
      "angle_designs": {"9": {"weights": [20 numbers]}, "30": {"weights": [20 numbers]}},
      "query_predictions": [[c_d, c_l], ...]
    }
  }
}
```

- `weights` are convex weights over the 20 base hulls in `data/glider_proxy.py` order: each ≥ 0, summing to 1 (tolerance 1e-4; renormalised).
- `pool_design.aoa_deg` must lie in [-30, 30].
- `query_predictions` has one `[c_d, c_l]` pair per entry of the instance's `queries.json`, in order, with `c_d > 0`.
- The result rows are named after `name`: `<name>` in `pool_efficiency` and `surrogate_validation`, and `<name minus _glider>_9deg` and `_30deg` in `angle_sweep_efficiency`. Use `ai_enhanced_glider` to be ranked against the reference rows.
- Other fields are ignored. Every scored number is recomputed from the weights, angles and predictions.

## Running

- `bash scripts/evaluate_train.sh` scores every artifact under `outputs/` on the development instances and writes `scoring/scores_train.json`. `bash scripts/evaluate.sh` writes the same scores to `scoring/scores.json`.
- The hidden test (`scripts/evaluate_test.sh`, no arguments) scores every artifact the same way on the held-out instances, against ground truth that exists only in the hidden evaluator. Ground truth is the error-free hydrodynamic response; the published labels are simulations of it with independent errors of a few percent per coefficient.

## Experiments and metrics

All metrics are means over the instances of the slice.

- `pool_efficiency`: the co-designed (hull, angle) pair, evaluated at the submitted angle. The `torpedo_baseline` row is the conventional torpedo hull at its own best angle. The evaluator fixes and computes it; it is not read from any artifact.
  - `efficiency_gain_over_torpedo` (primary, higher is better): design `eta` divided by the torpedo's best `eta` on the same instance.
  - `lift_to_drag` (higher is better).
  - `energy_per_distance_relative` (lower is better): `1 / eta`, capped at 100.
  - `trajectory_angle_deg` (lower is better): `atan(1 / eta)` in degrees; 90 when there is no lift.
- `angle_sweep_efficiency`: the 9° and 30° hulls, each evaluated at its angle. Same four metrics, with the torpedo at that same angle as the denominator.
- `surrogate_validation`: `surrogate_eta_abs_pct_error` (lower is better). For each query it is `|eta_pred − eta_true| / max(eta_true, 1) × 100`, capped at 100 and averaged. `eta_pred = max(c_l, 0) / c_d`.

## Validity rules

- A malformed or impossible value anywhere fails the whole artifact. That covers non-numeric or non-finite numbers, weights with a negative entry or a sum away from 1, an angle outside [-30, 30], a wrong-length prediction list, and `c_d ≤ 0`. Every scored metric of every experiment then takes its worst value (gain 0, eta 0, energy 100, glide angle 90, prediction error 100). Reasons are listed under `diagnostics.validity`.
- A missing instance, design or prediction list scores the worst value for that item.
- An unreadable artifact, or no artifact at all, scores the worst values.

`diagnostics.per_instance` lists the per-instance results; `diagnostics.instances` lists the torpedo reference values.

## Paper numbers

`scoring/reference.json` lists this benchmark's reference scores (the paper's method on the held-out instances) under `results`, and keeps the paper's reported results unchanged under each experiment's `_paper_reported`: pool-test lift-to-drag 2.5 (two-wing, 9°) and 2.4 (four-wing, 30°) versus 0.3 for a torpedo design from the literature, and 4.5% lift-to-drag error in wind-tunnel validation. Benchmark values are on the simulator's scale, not the physical pool scale, so compare against `scoring/scores_train.json` / `scores_test.json` rather than the paper's absolute numbers.
