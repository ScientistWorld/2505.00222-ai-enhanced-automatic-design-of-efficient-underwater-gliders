# Experiment Overview

## pool_efficiency
Tests whether a submitted glider design has better hydrodynamic efficiency than a conventional torpedo-shaped design. This is the central benchmark because the paper's main practical claim is that automated design can find more efficient underwater glider shapes.

The primary score is the dimensionless efficiency gain over the torpedo baseline. Raw lift-to-drag is also reported, but it is diagnostic because the paper's pool-test scale and this benchmark's local oracle scale are not identical.

## angle_sweep_efficiency
Tests whether efficient designs are found at multiple operating angles rather than only at the easiest single setting. This broadens the benchmark across the paper's two highlighted design conditions.

## Diagnostics
Score artifacts may include top-level diagnostic entries for method-side prediction agreement. These are audit values, not experiments, and are not part of the gym ranking.
