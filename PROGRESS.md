# Progress

## What Works

The paper has been analyzed and the workspace contains a faithful scaled computational pipeline: cage-parameter base shapes, interpolation, a 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES optimization constrained through convex combinations of base shapes.

CPU job `0fc2152a-5c4` ran the pipeline end-to-end and wrote method, baseline, checkpoint, and scoring artifacts. This supports the `method_runs` milestone.

## Results

Completed CPU test job results from the first run:
- Torpedo baseline lift-to-drag: 3.087
- Optimized design lift-to-drag: 5.535
- Optimized design energy per distance: 0.181
- Surrogate eta absolute percent error: 81.933

The optimized design improved over the baseline, but the surrogate prediction collapsed to a flat eta of 1.0. This is not strong enough for `core_claim` because the paper's workflow depends on a useful surrogate model.

Paper reference values captured in `scoring/reference.json`:
- Torpedo baseline pool-test lift-to-drag ratio: 0.3
- Optimized two-wing pool-test lift-to-drag ratio: 2.5
- Wind-tunnel validation average lift-to-drag error: 4.5 percent

## Remaining

Run a second containerized job after fixing target scaling in the neural surrogate. If the optimized design still beats the baseline and surrogate error is substantially reduced, update to `core_claim`.

## Issues

The paper does not release its 20 base meshes, deformation-cage fits, OpenFOAM cases, CFD label table, trained surrogate, optimized CAD files, wind-tunnel raw data, or pool telemetry. No public code release was found.

The first surrogate run collapsed because raw coefficient regression with the original high learning rate and a positive-output floor drove predictions to the floor. The implementation now standardizes lift/drag targets and unnormalizes predictions before CMA-ES scoring.

## Deviations from Paper

The paper used OpenFOAM-generated CFD labels for real cage-deformed meshes. Those labels and meshes are unavailable, so this reproduction uses a deterministic tracked hydrodynamic oracle in `data/glider_proxy.py` as the label source. The paper's algorithmic procedure is preserved: low-dimensional cage parameters, interpolation between base shapes, 4-layer tanh/batchnorm surrogate training, and CMA-ES optimization of lift-to-drag ratio.

The paper used 10 morphs per base-shape pair. This reproduction defaults to 3 morphs per pair to keep jobs small; the interpolation procedure is the same and can be scaled by changing `--morphs-per-pair`.
