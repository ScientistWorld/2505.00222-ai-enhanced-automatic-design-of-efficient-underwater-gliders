# Evaluation Protocol

The evaluator reads design artifacts from `outputs/<method>/optimization_results.json`. Each artifact must include:

- `shape`: normalized cage-parameter vector
- `aoa_deg`: selected angle of attack
- optional method-side predictions such as surrogate lift-to-drag

`scripts/evaluate.sh` calls only code in `eval/` and `data/`. It does not import the proposed method. The evaluator recomputes hydrodynamic coefficients and writes `scoring/scores.json`.

## Metrics

`pool_efficiency` is the primary benchmark. It compares the optimized design against a torpedo baseline.

- `efficiency_gain_over_torpedo`: higher is better and is the primary paper-facing metric. It is the candidate lift-to-drag ratio divided by the torpedo baseline lift-to-drag ratio under the same evaluator.
- `lift_to_drag`: higher is better and is reported as a raw diagnostic.
- `energy_per_distance_relative`: lower is better, computed as `1 / lift_to_drag`.
- `trajectory_angle_deg`: lower is better, computed as `atan(1 / lift_to_drag)` in degrees.

Reproduced scores are reported directly on the local CFD-like oracle scale. The paper reports pool-test values with a large simulation-to-reality gap, so `scoring/reference.json` records the paper's physical numbers while `scoring/scores.json` records the uncalibrated values produced by this reusable benchmark. This avoids fitting or hardcoding paper results into the evaluator.

`surrogate_validation` is a diagnostic check for methods that record their own efficiency prediction in the design artifact. Its metric coefficients are zero, so it is not part of the ranking; the benchmark also supports methods that do not expose an internal predictor.

- `lift_to_drag`: independent evaluated efficiency on the local oracle scale.
- `surrogate_lift_to_drag`: method-side predicted efficiency on the same local scale.
- `surrogate_eta_abs_pct_error`: lower is better.
- `raw_lift_to_drag` and `raw_surrogate_lift_to_drag`: duplicate the local-scale values for predictor/oracle agreement diagnostics.

The paper reports an optimized pool-test lift-to-drag ratio of 2.5 for its two-wing design and 2.4 for its four-wing design, versus 0.3 for a torpedo-shaped literature baseline. It also reports 4.5 percent average error in wind-tunnel validation of lift-to-drag ratio.
