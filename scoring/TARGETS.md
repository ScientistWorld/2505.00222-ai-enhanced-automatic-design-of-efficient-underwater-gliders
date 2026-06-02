# Evaluation Targets

## Primary: pool_efficiency
Tests whether an optimized glider design is more hydrodynamically efficient than the torpedo-shaped reference design under the same evaluation procedure.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- **Diagnostic metric**: `lift_to_drag` (higher is better)
- **Constraint metrics**: `energy_per_distance_relative` and `trajectory_angle_deg` (lower is better)

## Additional Setting: angle_sweep_efficiency
Tests whether optimized designs remain efficient at the two operating angles emphasized by the paper.
- **Primary metric**: `efficiency_gain_over_torpedo` (higher is better)
- **Diagnostic metric**: `lift_to_drag` (higher is better)

## Non-Target Diagnostics
Score artifacts may include top-level diagnostics, including prediction agreement for methods that report an internal hydrodynamic estimate. These diagnostics are not optimization targets and are not listed under `experiments`.

Run all targets with:

```bash
bash scripts/evaluate.sh
```
