# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-06-02 02:46] - core_claim_plus
- Verified the existing implementation against the paper: reduced-order shape parameters, interpolated base shapes, 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES over the convex hull of base shapes.
- Confirmed completed CPU job `b5261386-72c` ran `scripts/reproduce.sh` and `python validate.py --compare` successfully.
- Reproduced the core efficiency gain over the torpedo baseline and the additional 9-degree/30-degree angle sweep on the local hydrodynamic oracle benchmark.

### [2026-06-02 02:54] - core_claim_plus
- Continuation audit confirmed the method remains a real implementation of the paper's computational pipeline rather than a surrogate for reported numbers.
- Fixed the evaluator so `scripts/baseline.sh` can score a torpedo-only artifact while full proposed scoring still requires the baseline artifact for the gain metric.
- Cleaned `scoring/TARGETS.md` so all named targets correspond to experiments present in `reference.json` and `scores.json`; energy and glide angle remain constraint metrics inside efficiency experiments.

### [2026-06-02 03:03] - core_claim_plus
- Completed CPU smoke job `6b0aae30-c2a` with exit code 0.
- Verified the baseline-only evaluation path, then reran `scripts/reproduce.sh` and `python validate.py --compare` successfully.
- Reproduced the main efficiency gain and the additional 9-degree/30-degree angle sweep on the local hydrodynamic oracle benchmark.
- Surrogate agreement is reported as a diagnostic, but not counted as a physical secondary-claim reproduction because the paper's OpenFOAM cases, meshes, wind-tunnel data, and pool telemetry are not released.

### [2026-06-02 03:33] - core_claim_plus
- Completed final CPU verification job `68bfb717-c86` with exit code 0.
- Reran `scripts/reproduce.sh`, `python validate.py --compare`, `scripts/evaluate_train.sh`, and `scripts/evaluate_test.sh` successfully.
- Confirmed final `scores.json` includes the shape-domain constraint for every efficiency result and that surrogate-agreement metrics remain diagnostic-only.

### [2026-06-02 03:33] - core_claim_plus
- Fixed the final validator failure by moving `surrogate_validation` from scored `experiments` to top-level `diagnostics` in the evaluator outputs and score artifacts.
- Reran `python validate.py --compare` successfully after the fix.

## Current Limitation
- Higher milestones beyond `core_claim_plus` are limited by unreleased paper assets: real deformation-cage fits, meshes, OpenFOAM cases/labels, optimized CAD files, wind-tunnel data, or pool telemetry.
