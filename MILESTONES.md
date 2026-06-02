# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-06-02 02:10] - none
- Read the paper and identified the core method: reduced-order deformation-cage shape representation, neural fluid surrogate, and CMA-ES shape/control optimization.
- Found no public code release or released CFD/cage datasets.
- Implemented the scaled reproduction pipeline and prepared a containerized run, but no compute job has completed yet.

### [2026-06-02 02:20] - method_runs
- CPU test job `0fc2152a-5c4` completed successfully.
- The full pipeline ran end-to-end: torpedo baseline, neural fluid surrogate training, CMA-ES optimization at 9 and 30 degrees, and evaluator scoring.
- The optimized design beat the torpedo baseline under the independent evaluator, but surrogate validation was poor, so the next run improves target scaling before claiming `core_claim`.

## Stop Justification
- Not stopped.
