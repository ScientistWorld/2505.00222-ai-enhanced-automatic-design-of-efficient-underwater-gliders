# Experiment Overview

## pool_efficiency
Tests whether the reproduced design process produces a glider with better hydrodynamic efficiency than a conventional torpedo-shaped design. This is the central benchmark because the paper's main practical claim is that automated design finds more efficient underwater glider shapes.

The primary score is the dimensionless efficiency gain over the torpedo baseline. Raw lift-to-drag is also reported, but it is diagnostic because the paper's pool-test scale and this benchmark's local oracle scale are not identical.

## surrogate_validation
Reports whether a submitted method-side hydrodynamic prediction agrees with an independent evaluation. Its metric coefficients are zero, so it is diagnostic rather than part of the ranking; the reusable benchmark must also support methods that do not expose an internal predictor.

## angle_sweep_efficiency
Tests whether efficient designs are found at multiple operating angles rather than only at the easiest single setting. This broadens the benchmark across the paper's two highlighted design conditions.
