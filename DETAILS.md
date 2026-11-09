# Overview

This workspace reproduces the core computational claim of *AI-Enhanced Automatic Design of Efficient Underwater Gliders*: a reduced-order shape representation plus a neural hydrodynamic surrogate and CMA-ES can discover glider hulls with better lift-to-drag efficiency than a manually designed torpedo-like baseline.

The unreleased physical and CFD assets are replaced by a deterministic benchmark oracle, while the algorithmic pipeline remains the paper's: shared cage parameters, interpolated shapes, 4-layer tanh/batchnorm surrogate, and convex-hull-constrained CMA-ES shape optimization across angle-of-attack settings.

---

# Problem Definition

Design an autonomous underwater glider hull and operating angle of attack that maximizes hydrodynamic efficiency. Efficiency is measured by the nondimensional lift-to-drag ratio:

`eta = c_l / c_d`

where `c_l` is the lift coefficient and `c_d` is the drag coefficient for the candidate hull at the selected angle of attack.

The reusable benchmark represents each hull by a fixed low-dimensional vector of normalized shape parameters. The evaluation problem is to output a valid shape vector and an angle of attack in degrees. The design must be evaluated by the same hydrodynamic oracle used by the benchmark, and compared against a torpedo-like glider baseline under the same procedure.

Success requires improving lift-to-drag ratio while also reducing the implied energy per horizontal distance and maintaining a shallow glide trajectory. Invalid designs, out-of-range shape coordinates, or designs that only exploit a prediction model without improving under the independent evaluator do not solve the problem.

---

# Paper Method

The paper proposes an automated glider co-design pipeline.

First, hull geometry is represented by a reduced-order 3D deformation cage around an ellipsoid. The paper curated 20 base shapes from marine animals and underwater or aerodynamic vehicles, fit each to the same cage parameterization, and interpolated between base-shape pairs to expand the design dataset.

Second, the paper generated hydrodynamic labels with OpenFOAM. For each cage-parameterized shape and angle of attack, OpenFOAM computed drag and lift coefficients.

Third, a neural fluid surrogate maps cage parameters plus angle of attack to `c_d` and `c_l`. The surrogate is a 4-layer MLP with batch normalization and `tanh` activations, trained with MSE loss using Adam, learning rate 0.1, batch size 128, 10 warmup epochs, and 200 total epochs.

Finally, the trained surrogate is used inside covariance matrix adaptation evolution strategy (CMA-ES). For each angle of attack, CMA-ES searches shape parameters constrained to the convex hull of the base shapes and maximizes `eta = c_l / c_d`. The paper fabricated selected optima at 9 degrees and 30 degrees.

## Reproduction Notes

The paper does not release the base meshes, deformation-cage fits, OpenFOAM cases, CFD labels, or trained checkpoint. This reproduction keeps the paper's computational steps but replaces the unreleased CFD label source with a deterministic, tracked hydrodynamic oracle in `data/`. The method code still trains the specified neural surrogate and optimizes with CMA-ES over convex combinations of base cage vectors.

---

# Evaluation Protocol

The evaluator reads design artifacts from `outputs/<method>/optimization_results.json`. Each artifact must include:

- `shape`: normalized shape-parameter vector
- `aoa_deg`: selected angle of attack
- optional method-side estimates of lift-to-drag for diagnostics

`scripts/evaluate.sh` calls only code in `eval/` and `data/`. It does not import any submitted method. The evaluator recomputes hydrodynamic coefficients and writes `scoring/scores.json`.

## Metrics

`pool_efficiency` is the primary benchmark. It compares a submitted design against a torpedo baseline.

- `efficiency_gain_over_torpedo`: higher is better and is the primary benchmark metric. It is the candidate lift-to-drag ratio divided by the torpedo baseline lift-to-drag ratio under the same evaluator.
- `lift_to_drag`: higher is better and is reported as a raw diagnostic.
- `energy_per_distance_relative`: lower is better, computed as `1 / lift_to_drag`.
- `trajectory_angle_deg`: lower is better, computed as `atan(1 / lift_to_drag)` in degrees.

Reproduced scores are reported directly on the local CFD-like oracle scale. The paper reports pool-test values with a large simulation-to-reality gap, so `scoring/reference.json` records the paper's physical numbers while `scoring/scores.json` records the uncalibrated values produced by this reusable benchmark. This avoids fitting or hardcoding paper results into the evaluator.

Top-level diagnostics may check whether a method's recorded efficiency estimate agrees with independent evaluation. Diagnostic metric coefficients are zero, so these values are not part of the ranking; the benchmark also supports methods that do not expose an internal predictor.

- `lift_to_drag`: independent evaluated efficiency on the local oracle scale.
- method-side predicted efficiency on the same local scale, when provided.
- absolute percentage error between method-side and evaluator-side efficiency, when provided.

The paper reports an optimized pool-test lift-to-drag ratio of 2.5 for its two-wing design and 2.4 for its four-wing design, versus 0.3 for a torpedo-shaped literature baseline. It also reports 4.5 percent average error in wind-tunnel validation of lift-to-drag ratio.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 10m | **GPU**: 0.0h
- **Jobs**: 3 total (3 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 2m | **GPU**: 0.0h
- **Jobs**: 4 total (4 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-02 00:00] - core_claim_plus
- Implemented the paper's reduced-order cage-parameter surrogate workflow at accessible scale.
- Trained a 4-layer tanh/batchnorm neural fluid surrogate on interpolated cage designs with angle-of-attack inputs.
- Ran CMA-ES over convex combinations of base cage vectors for the fabricated 9-degree and 30-degree operating settings.
- Reproduced the central efficiency gain over the torpedo baseline and added an angle-sweep constraint/benefit score.

### [2026-06-02 02:36] - core_claim_plus
- Completed audit-fix job `b5261386-72c` after removing paper-fitted score calibration from the evaluator.
- Regenerated uncalibrated local-oracle scores: optimized 9-degree lift-to-drag 9.708 vs torpedo 0.982, and optimized 30-degree lift-to-drag 6.238.
- `python validate.py --compare` passed all scoring and separation checks.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 15m | **GPU**: 0.0h
- **Jobs**: 5 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 5 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 5 total (5 completed, 0 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 7 total (6 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `secondary_claims` | **Status**: done
- **Working time**: 2m | **GPU**: 0.0h
- **Jobs**: 7 total (6 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 8 total (7 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-02 02:46] - core_claim_plus
- Verified the existing implementation against the paper: reduced-order cage parameters, interpolated base shapes, 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES over the convex hull of base shapes.
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
- Confirmed final `scores.json` includes the cage feature-range constraint for every efficiency result and that surrogate-agreement metrics remain diagnostic-only.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 7m | **GPU**: 0.0h
- **Jobs**: 9 total (8 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-06-02 03:46] - core_claim_plus
- Completed final managed-container CPU smoke job `b01de9c2-b2b` with exit code 0.
- Reran `scripts/evaluate.sh`, `python validate.py --compare`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and a final `python validate.py --compare` successfully.
- Confirmed the workspace is ready for gym use at `core_claim_plus` after method-agnostic documentation and scoring cleanup.

</details>

### Iteration 10: gpt-6.1-sol (redteam)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 12m | **GPU**: 0.0h
- **Jobs**: 9 total (8 completed, 1 failed)

<details>
<summary>Progress Log</summary>

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

### [2026-06-02 03:46] - core_claim_plus
- Completed final managed-container CPU smoke job `b01de9c2-b2b` with exit code 0.
- Reran `scripts/evaluate.sh`, `python validate.py --compare`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and a final `python validate.py --compare` successfully.
- Confirmed the workspace is ready for gym use at `core_claim_plus` after method-agnostic documentation and scoring cleanup.

</details>


---

# Reproduction Milestones

**Current: core_claim_plus**
