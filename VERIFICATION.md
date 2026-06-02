# Verification Report

## Initial Assessment
The workspace started final verification at `core_claim_plus`. That milestone is justified: the implementation runs the paper's computational design pipeline at local benchmark scale, and prior CPU jobs successfully ran the reproduction, train/test evaluators, and `validate.py --compare`.

The workspace is not a physical or CFD-data reproduction. The paper's base meshes, deformation fits, OpenFOAM cases/labels, optimized CAD, wind-tunnel measurements, and pool telemetry are not released, so the gym uses a deterministic tracked hydrodynamic evaluator in `data/`.

## Issues Found
- Minor: Method-agnostic documentation and one scored constraint metric used paper-specific "cage" wording. This could unnecessarily steer from-scratch agents toward the paper's representation.
- Minor: The existing `VERIFICATION.md` was stale and referred to an earlier milestone audit.
- Minor: Tracked `trajectory/` logs were already deleted in the worktree. They are generated workflow artifacts and should not ship with the gym.

## Fixes Applied
- Renamed the scored validity metric from `cage_feature_range_violation` to `shape_domain_violation` across `reference.json`, score artifacts, and evaluators. The computation is unchanged.
- Reworded method-agnostic documentation in `briefing/problem.md`, `briefing/evaluation.md`, `scoring/EXPERIMENTS.md`, `scoring/TARGETS.md`, `scoring/CONSTRAINTS.md`, and `scoring/DIRECTION.md`.
- Removed stale generated trajectory logs from git.
- Ran `python validate.py --compare` locally after the changes; it passed.
- Ran final CPU smoke job `b01de9c2-b2b` in the managed container. It completed with exit code 0 after running `scripts/evaluate.sh`, `python validate.py --compare`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and a final `python validate.py --compare`. The job confirmed evaluator independence from `method/`, no committed `shared/` paths, train/test rewiring, train/test method-key consistency, and primary-metric discrimination.

## Final Judgment
The workspace is ready to serve as a research gym in both improve and from-scratch modes. Problem/evaluation documentation is method-agnostic, scored metrics reward the scientific objective and constraints rather than fit-to-paper error, and the standard plus train/test evaluators run inside the managed container.

- Milestone: core_claim_plus
- Ready for gym use: yes
- Confidence: high
- Key limitation: Substitute hydrodynamic oracle because the paper's CFD and physical-test assets are unreleased.
