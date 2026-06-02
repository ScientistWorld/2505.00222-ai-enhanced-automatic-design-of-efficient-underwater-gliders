# Experiment Overview

## pool_efficiency
Tests whether the reproduced design process produces a glider with better hydrodynamic efficiency than a conventional torpedo-shaped design. This is the central benchmark because the paper's main practical claim is that automated design finds more efficient underwater glider shapes.

The primary score is the dimensionless efficiency gain over the torpedo baseline. Raw lift-to-drag is also reported, but it is diagnostic because the paper's pool-test scale and this benchmark's local oracle scale are not identical.

## surrogate_validation
Tests whether the predicted hydrodynamic performance for the selected design agrees with an independent evaluation. This guards against methods that over-optimize a predictor without producing a design that remains efficient when rescored.

## angle_sweep_efficiency
Tests whether efficient designs are found at multiple operating angles rather than only at the easiest single setting. This broadens the benchmark across the paper's two highlighted design conditions.
