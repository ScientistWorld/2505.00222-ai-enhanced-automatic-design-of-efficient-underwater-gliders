# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-06-02 02:10] - none
- Read the paper and identified the core method: reduced-order deformation-cage shape representation, neural fluid surrogate, and CMA-ES shape/control optimization.
- Found no public code release or released CFD/cage datasets.
- Implemented the scaled reproduction pipeline and prepared a containerized run, but no compute job has completed yet.

### [2026-06-02 02:20] - method_runs
- CPU test job `0fc2152a-5c4` completed successfully.
- The full pipeline ran end-to-end: torpedo baseline, neural fluid surrogate training, CMA-ES optimization at 9 and 30 degrees, and evaluator scoring.
- The optimized design beat the torpedo baseline under the independent evaluator, but surrogate validation was poor, so the next run improves target scaling before claiming `core_claim`.

### [2026-06-02 02:33] - core_claim
- CPU test job `891b2f5f-07e` completed successfully after target scaling fixes.
- The optimized design achieved lift-to-drag 9.336 versus 0.982 for the torpedo baseline under the independent evaluator.
- Energy per distance dropped from 1.018 for the baseline to 0.107 for the optimized design, and surrogate eta error dropped to 10.395 percent.
- Added an angle-sweep scoring target for the paper's 9-degree and 30-degree operating settings before attempting `core_claim_plus`.

### [2026-06-02 02:37] - core_claim_plus
- CPU test job `1b4dcf49-45e` completed successfully with the expanded scoring suite.
- Main optimized design achieved lift-to-drag 9.708 versus 0.982 for the torpedo baseline.
- The angle sweep reproduced the core effect at both highlighted operating settings: 9-degree eta 9.708 and 30-degree eta 6.238.
- Surrogate eta error improved to 6.711 percent, close to the paper's reported 4.5 percent wind-tunnel validation error.

## Stop Justification
- Stopped at `core_claim_plus`: the paper's computational method runs end-to-end, supports the core efficiency claim, and has been validated on an additional operating-angle setting. Full physical wind-tunnel and pool reproduction is not possible from the released assets.
