# Paper Method

The paper proposes an automated glider co-design pipeline.

First, hull geometry is represented by a reduced-order 3D deformation cage around an ellipsoid. The paper curated 20 base shapes from marine animals and underwater or aerodynamic vehicles, fit each to the same cage parameterization, and interpolated between base-shape pairs to expand the design dataset (ten morphs per pair).

Second, the paper generated hydrodynamic labels with OpenFOAM. For each cage-parameterized shape and each of five angles of attack between -30 and +30 degrees, OpenFOAM computed drag and lift coefficients.

Third, a neural fluid surrogate maps cage parameters plus angle of attack to `c_d` and `c_l`. The surrogate is a 4-layer MLP with batch normalization and `tanh` activations, trained with MSE loss using Adam, learning rate 0.1, batch size 128, 10 warmup epochs, and 200 total epochs.

Finally, the trained surrogate is used inside covariance matrix adaptation evolution strategy (CMA-ES). For each angle of attack, CMA-ES is initialised at the average of the training shapes, searches shape parameters constrained to the convex hull of the base shapes, maximizes `eta = c_l / c_d`, and is repeated several times. The best design per angle traces an efficiency-versus-angle curve; the paper fabricated the optima at 9 degrees and 30 degrees.

## Reproduction Notes

The paper does not release the base meshes, deformation-cage fits, OpenFOAM cases, CFD labels, or trained checkpoint. This benchmark keeps the paper's computational steps but replaces the CFD label source with deterministic synthetic fluid instances (hidden ground truth, public labelled datasets of the paper's size: 20 bases + 10 morphs per pair at 5 angles). The reference implementation (`method/`) trains the specified surrogate per instance on exactly that dataset, runs CMA-ES on softmax-parameterised convex weights from the average shape at angles 0, 3, ..., 30 degrees with 3 repeats each, and picks designs (and the co-design angle) by surrogate prediction only.
