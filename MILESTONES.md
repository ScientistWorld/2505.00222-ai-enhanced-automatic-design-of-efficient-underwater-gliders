# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-06-02 02:46] - core_claim_plus
- Verified the existing implementation against the paper: reduced-order cage parameters, interpolated base shapes, 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES over the convex hull of base shapes.
- Confirmed completed CPU job `b5261386-72c` ran `scripts/reproduce.sh` and `python validate.py --compare` successfully.
- Reproduced the core efficiency gain over the torpedo baseline and the additional 9-degree/30-degree angle sweep on the local hydrodynamic oracle benchmark.

## Stop Justification
- Completed at milestone `core_claim_plus`.
- Higher milestones would require unreleased paper assets: real deformation-cage fits, meshes, OpenFOAM cases/labels, optimized CAD files, wind-tunnel data, or pool telemetry.
