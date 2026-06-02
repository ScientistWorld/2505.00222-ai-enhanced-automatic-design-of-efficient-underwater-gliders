# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-06-02 00:00] - core_claim_plus
- Implemented the paper's reduced-order cage-parameter surrogate workflow at accessible scale.
- Trained a 4-layer tanh/batchnorm neural fluid surrogate on interpolated cage designs with angle-of-attack inputs.
- Ran CMA-ES over convex combinations of base cage vectors for the fabricated 9-degree and 30-degree operating settings.
- Reproduced the central efficiency gain over the torpedo baseline and added an angle-sweep constraint/benefit score.
