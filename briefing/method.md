# Paper Method

The paper proposes an automated glider co-design pipeline.

First, hull geometry is represented by a reduced-order 3D deformation cage around an ellipsoid. The paper curated 20 base shapes from marine animals and underwater or aerodynamic vehicles, fit each to the same cage parameterization, and interpolated between base-shape pairs to expand the design dataset.

Second, the paper generated hydrodynamic labels with OpenFOAM. For each cage-parameterized shape and angle of attack, OpenFOAM computed drag and lift coefficients.

Third, a neural fluid surrogate maps cage parameters plus angle of attack to `c_d` and `c_l`. The surrogate is a 4-layer MLP with batch normalization and `tanh` activations, trained with MSE loss using Adam, learning rate 0.1, batch size 128, 10 warmup epochs, and 200 total epochs.

Finally, the trained surrogate is used inside covariance matrix adaptation evolution strategy (CMA-ES). For each angle of attack, CMA-ES searches shape parameters constrained to the convex hull of the base shapes and maximizes `eta = c_l / c_d`. The paper fabricated selected optima at 9 degrees and 30 degrees.

## Reproduction Notes

The paper does not release the base meshes, deformation-cage fits, OpenFOAM cases, CFD labels, or trained checkpoint. This reproduction keeps the paper's computational steps but replaces the unreleased CFD label source with a deterministic, tracked hydrodynamic oracle in `data/`. The method code still trains the specified neural surrogate and optimizes with CMA-ES over convex combinations of base cage vectors.
