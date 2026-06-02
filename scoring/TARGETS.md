# Evaluation Targets

## Primary: pool_efficiency
Tests whether an optimized glider design is more hydrodynamically efficient than the torpedo-shaped reference design under the same evaluation procedure.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- **Diagnostic metric**: `lift_to_drag` (higher is better)
- **Constraint metrics**: `energy_per_distance_relative` and `trajectory_angle_deg` (lower is better)

## Diagnostic: surrogate_validation
Reports whether a submitted method-side efficiency prediction remains aligned with an independent hydrodynamic evaluation of the selected design. This experiment has zero ranking coefficients because methods without an internal predictor could otherwise game or omit this field.
- **Metric**: `surrogate_eta_abs_pct_error` (lower is better, diagnostic only)

## Additional Setting: angle_sweep_efficiency
Tests whether optimized designs remain efficient at the two operating angles emphasized by the paper.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- **Diagnostic metric**: `lift_to_drag` (higher is better)

Run all targets with:

```bash
bash scripts/evaluate.sh
```
