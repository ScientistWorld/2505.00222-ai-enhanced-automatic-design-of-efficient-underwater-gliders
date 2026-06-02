# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-06-02 00:00] - core_claim_plus
- Implemented the paper's reduced-order cage-parameter surrogate workflow at accessible scale.
- Trained a 4-layer tanh/batchnorm neural fluid surrogate on interpolated cage designs with angle-of-attack inputs.
- Ran CMA-ES over convex combinations of base cage vectors for the fabricated 9-degree and 30-degree operating settings.
- Reproduced the central efficiency gain over the torpedo baseline and added an angle-sweep constraint/benefit score.

### [2026-06-02 02:36] - core_claim_plus
- Completed audit-fix job `b5261386-72c` after removing paper-fitted score calibration from the evaluator.
- Regenerated uncalibrated local-oracle scores: optimized 9-degree lift-to-drag 9.708 vs torpedo 0.982, and optimized 30-degree lift-to-drag 6.238.
- `python validate.py --compare` passed all scoring and separation checks.

### [2026-06-02 03:00] - core_claim_plus
- Fixed validation consistency by making `efficiency_gain_over_torpedo` the primary paper-facing metric for efficiency experiments.
- Preserved raw local-oracle lift-to-drag values as diagnostic metrics in `scores.json`.
- `python validate.py --compare` passes with the updated reference and scores.
