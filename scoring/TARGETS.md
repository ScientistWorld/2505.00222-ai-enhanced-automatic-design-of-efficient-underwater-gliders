# Evaluation Targets

## Primary: pool_efficiency
Co-designed hull and angle of attack versus the torpedo hull at its best angle, per fluid instance.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- **Benefit metric**: `lift_to_drag` (higher is better)
- **Energy/trajectory metrics**: `energy_per_distance_relative`, `trajectory_angle_deg` (lower is better)

## angle_sweep_efficiency
Hulls for the paper's two fabricated operating angles, 9° (`*_9deg`) and 30° (`*_30deg`), each versus the torpedo at that angle.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- Same four metrics as above.

## surrogate_validation
Prediction accuracy on the evaluator's held-out query hulls and angles.
- **Primary metric**: `surrogate_eta_abs_pct_error` (lower is better; missing predictions score 100)

## Constraints (gates)
- Designs are convex weights over the base-hull library (inside the convex hull). The pool angle lies in [-30°, 30°].
- Any violation or impossible value (non-finite numbers, negative weights, `c_d ≤ 0`, wrong lengths) fails the run, and every metric of every experiment gets its worst value.

Run the development slice with:

```bash
bash scripts/evaluate_train.sh
```
