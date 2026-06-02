# Evaluation Protocol

The evaluator reads design artifacts from `outputs/<method>/optimization_results.json`. Each artifact must include:

- `shape`: normalized cage-parameter vector
- `aoa_deg`: selected angle of attack
- optional method-side predictions such as surrogate lift-to-drag

`scripts/evaluate.sh` calls only code in `eval/` and `data/`. It does not import the proposed method. The evaluator recomputes hydrodynamic coefficients and writes `scoring/scores.json`.

## Metrics

`pool_efficiency` is the primary benchmark. It compares the optimized design against a torpedo baseline.

- `lift_to_drag`: higher is better.
- `energy_per_distance_relative`: lower is better, computed as `1 / lift_to_drag`.
- `trajectory_angle_deg`: lower is better, computed as `atan(1 / lift_to_drag)` in degrees.

Pool-facing experiments report lift-to-drag on the paper's pool-test scale. The local oracle is CFD-like, while the paper reports a clear simulation-to-pool gap, so the evaluator applies a monotonic calibration fitted to the paper's torpedo baseline and 9-degree optimized pool result. Raw oracle values remain available in the surrogate-validation experiment.

`surrogate_validation` checks that the selected design is not only good according to its internal prediction model.

- `lift_to_drag`: pool-equivalent independent evaluated efficiency.
- `surrogate_lift_to_drag`: pool-equivalent method-side predicted efficiency.
- `surrogate_eta_abs_pct_error`: lower is better.
- `raw_lift_to_drag` and `raw_surrogate_lift_to_drag`: raw CFD-like values for predictor/oracle agreement diagnostics.

The paper reports an optimized pool-test lift-to-drag ratio of 2.5 for its two-wing design and 2.4 for its four-wing design, versus 0.3 for a torpedo-shaped literature baseline. It also reports 4.5 percent average error in wind-tunnel validation of lift-to-drag ratio.
