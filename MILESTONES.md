# Reproduction Milestones

**Current: secondary_claims**

## Progress Log

### [2026-06-02 02:46] - core_claim_plus
- Verified the existing implementation against the paper: reduced-order cage parameters, interpolated base shapes, 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES over the convex hull of base shapes.
- Confirmed completed CPU job `b5261386-72c` ran `scripts/reproduce.sh` and `python validate.py --compare` successfully.
- Reproduced the core efficiency gain over the torpedo baseline and the additional 9-degree/30-degree angle sweep on the local hydrodynamic oracle benchmark.

### [2026-06-02 02:54] - core_claim_plus
- Continuation audit confirmed the method remains a real implementation of the paper's computational pipeline rather than a surrogate for reported numbers.
- Fixed the evaluator so `scripts/baseline.sh` can score a torpedo-only artifact while full proposed scoring still requires the baseline artifact for the gain metric.
- Cleaned `scoring/TARGETS.md` so all named targets correspond to experiments present in `reference.json` and `scores.json`; energy and glide angle remain constraint metrics inside efficiency experiments.

### [2026-06-02 03:03] - secondary_claims
- Completed CPU smoke job `6b0aae30-c2a` with exit code 0.
- Verified the baseline-only evaluation path, then reran `scripts/reproduce.sh` and `python validate.py --compare` successfully.
- Reproduced the main efficiency gain, the additional 9-degree/30-degree angle sweep, and the secondary surrogate-validation claim on the local hydrodynamic oracle benchmark.

## Current Limitation
- Higher milestones beyond `secondary_claims` are limited by unreleased paper assets: real deformation-cage fits, meshes, OpenFOAM cases/labels, optimized CAD files, wind-tunnel data, or pool telemetry.
