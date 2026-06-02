# Progress

## What Works

The paper has been analyzed and the workspace now contains a faithful scaled computational pipeline: cage-parameter base shapes, interpolation, a 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES optimization constrained through convex combinations of base shapes.

The reusable evaluator reads design artifacts from `outputs/` and computes benchmark metrics without importing `method/`.

## Results

No compute job has completed yet in this reproduction. The next submitted job will run the full pipeline and write `scoring/scores.json`.

Paper reference values captured in `scoring/reference.json`:
- Torpedo baseline pool-test lift-to-drag ratio: 0.3
- Optimized two-wing pool-test lift-to-drag ratio: 2.5
- Wind-tunnel validation average lift-to-drag error: 4.5 percent

## Remaining

Run the containerized reproduction job, inspect `scoring/scores.json`, compare with `python validate.py --compare`, and then update the milestone based on the completed job result.

## Issues

The paper does not release its 20 base meshes, deformation-cage fits, OpenFOAM cases, CFD label table, trained surrogate, optimized CAD files, wind-tunnel raw data, or pool telemetry. No public code release was found.

The login-node Python environment lacks numerical dependencies such as `numpy`; runtime validation is therefore deferred to the submitted container, where `environment/setup.sh` installs dependencies.

## Deviations from Paper

The paper used OpenFOAM-generated CFD labels for real cage-deformed meshes. Those labels and meshes are unavailable, so this reproduction uses a deterministic tracked hydrodynamic oracle in `data/glider_proxy.py` as the label source. The paper's algorithmic procedure is preserved: low-dimensional cage parameters, interpolation between base shapes, 4-layer tanh/batchnorm surrogate training, and CMA-ES optimization of lift-to-drag ratio.

The paper used 10 morphs per base-shape pair. This reproduction defaults to 3 morphs per pair to keep the first compute job small; the interpolation procedure is the same and can be scaled by changing `--morphs-per-pair`.
