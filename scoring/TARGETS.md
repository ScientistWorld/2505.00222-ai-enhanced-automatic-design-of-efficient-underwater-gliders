# Evaluation Targets

## Primary: pool_efficiency
Tests whether an optimized glider design is more hydrodynamically efficient than the torpedo-shaped reference design under the same evaluation procedure.
- **Metric**: `lift_to_drag` (higher is better)

## Constraint: energy_and_glide_angle
Tests whether the efficiency gain also reduces the implied energy required per distance and produces a shallower glide trajectory.
- **Metrics**: `energy_per_distance_relative` and `trajectory_angle_deg` (lower is better)

## Constraint: surrogate_validation
Tests whether the method-side predicted efficiency remains aligned with an independent hydrodynamic evaluation of the selected design.
- **Metric**: `surrogate_eta_abs_pct_error` (lower is better)

Run all targets with:

```bash
bash scripts/evaluate.sh
```
