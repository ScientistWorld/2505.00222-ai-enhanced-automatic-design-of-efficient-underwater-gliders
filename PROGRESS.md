# Progress

## What Works

The paper has been analyzed and the workspace contains a faithful scaled computational pipeline: cage-parameter base shapes, interpolation, a 4-layer tanh/batchnorm neural fluid surrogate, and CMA-ES optimization constrained through convex combinations of base shapes.

CPU jobs `0fc2152a-5c4`, `891b2f5f-07e`, and `1b4dcf49-45e` ran the initial pipeline end-to-end and wrote method, baseline, checkpoint, and scoring artifacts. Continuation job `b5261386-72c` reran the full pipeline after the evaluator audit fix and validated `core_claim_plus`. Continuation smoke job `6b0aae30-c2a` verified baseline-only scoring, reran the full reproduction, and validated the current `core_claim_plus` milestone.

Continuation audit on 2026-06-02 confirmed that `method/` implements the paper's algorithmic steps and that `eval/` remains independent from `method/`. The audit found and fixed two packaging issues: baseline-only scoring no longer depends on an existing proposed artifact, and `scoring/TARGETS.md` no longer names an experiment absent from `reference.json` and `scores.json`.

## Results

Completed CPU test job results from the first run:
- Torpedo baseline lift-to-drag: 3.087
- Optimized design lift-to-drag: 5.535
- Optimized design energy per distance: 0.181
- Surrogate eta absolute percent error: 81.933

Completed CPU test job results after surrogate target scaling:
- Torpedo baseline lift-to-drag: 0.982
- Optimized design lift-to-drag: 9.336
- Optimized design energy per distance: 0.107
- Surrogate eta absolute percent error: 10.395

The optimized design improves strongly over the baseline and preserves the paper's benefit/constraint structure, so `core_claim` is reached.

Completed CPU test job with expanded angle-sweep scoring before pool-scale calibration:
- Torpedo baseline lift-to-drag: 0.982
- Best optimized design lift-to-drag: 9.708
- Best optimized design energy per distance: 0.103
- Surrogate eta absolute percent error: 6.711
- Optimized 9-degree lift-to-drag: 9.708
- Optimized 30-degree lift-to-drag: 6.238

Both highlighted operating-angle settings outperform the torpedo baseline on the raw proxy metric.

Continuation audit found that the previous evaluator calibrated raw CFD-like oracle eta values onto paper pool-test eta using paper constants. That made the 9-degree result match the paper by construction, so the evaluator was fixed to report direct uncalibrated oracle scores from method artifacts. The current honest local-scale scores are:
- Torpedo baseline lift-to-drag: 0.982
- Optimized 9-degree lift-to-drag: 9.708
- Optimized 30-degree lift-to-drag: 6.238
- Surrogate eta absolute percent error: 6.711
- Primary pool-efficiency gain over torpedo: 9.884 reproduced vs 8.333 reported by the paper
- Primary 30-degree gain over torpedo: 6.351 reproduced vs 8.000 reported by the paper

This restores `core_claim_plus`: the reproduced method shows the claimed large efficiency improvement on the main 9-degree setting and remains above baseline on the additional 30-degree setting. The numbers are not on the same physical pool-test scale as the paper because the paper's meshes, OpenFOAM labels, fabrication details, and telemetry are not released.

Completed CPU smoke job `6b0aae30-c2a` confirmed the final scores:
- Torpedo baseline lift-to-drag: 0.982
- Optimized glider lift-to-drag: 9.708
- Optimized glider gain over torpedo: 9.884 vs 8.333 reported by the paper
- Optimized 30-degree gain over torpedo: 6.351 vs 8.000 reported by the paper
- Surrogate eta absolute percent error: 6.711 percent vs 4.5 percent reported by the paper

This supports `core_claim_plus`: the main efficiency gain is reproduced on the local oracle benchmark, and the method also improves over the torpedo baseline at the additional 30-degree operating-angle setting. Surrogate agreement is reported as a diagnostic, but not counted as a physical secondary-claim reproduction because the paper's real CFD and experimental assets are unavailable.

Paper reference values captured in `scoring/reference.json`:
- Torpedo baseline pool-test lift-to-drag ratio: 0.3
- Optimized two-wing pool-test lift-to-drag ratio: 2.5
- Wind-tunnel validation average lift-to-drag error: 4.5 percent

## Remaining

No required work remains for the packaged `core_claim_plus` reproduction. Higher milestones would require unavailable physical assets or a more complete substitute for the paper's unreleased OpenFOAM/mesh dataset.

## Issues

The paper does not release its 20 base meshes, deformation-cage fits, OpenFOAM cases, CFD label table, trained surrogate, optimized CAD files, wind-tunnel raw data, or pool telemetry. No public code release was found.

The first surrogate run collapsed because raw coefficient regression with the original high learning rate and a positive-output floor drove predictions to the floor. The implementation now standardizes lift/drag targets, unnormalizes predictions before CMA-ES scoring, and saves the best validation checkpoint.

The final job emitted a `cma.plot()` matplotlib warning from the optional CMA plotting module. It does not affect training, optimization, or scoring.

## Deviations from Paper

The paper used OpenFOAM-generated CFD labels for real cage-deformed meshes. Those labels and meshes are unavailable, so this reproduction uses a deterministic tracked hydrodynamic oracle in `data/glider_proxy.py` as the label source. The paper's algorithmic procedure is preserved: low-dimensional cage parameters, interpolation between base shapes, 4-layer tanh/batchnorm surrogate training, and CMA-ES optimization of lift-to-drag ratio. Evaluation reports this local oracle scale directly rather than calibrating to the paper's pool-test values.

The paper used 10 morphs per base-shape pair. This reproduction defaults to 3 morphs per pair to keep jobs small; the interpolation procedure is the same and can be scaled by changing `--morphs-per-pair`.

## Latest Job

Job `b5261386-72c` completed successfully with exit code 0 on 0 GPUs. It reran `scripts/reproduce.sh` and `python validate.py --compare`; all validation checks passed. The only stderr output was a warning that matplotlib is not installed for optional `cma.plot()` functionality, which is unused by the reproduction.

Post-job validation tightened paper consistency checks for primary metrics. The paper-facing primary metric for efficiency experiments is now `efficiency_gain_over_torpedo`, which is dimensionless and comparable between the paper's pool scale and this reproduction's local oracle scale. Raw lift-to-drag remains in `scores.json` as a diagnostic and constraint metric.

Job `6b0aae30-c2a` completed successfully with exit code 0 on 0 GPUs. It first verified that a torpedo-only artifact can be scored through `scripts/evaluate.sh`, then reran `scripts/reproduce.sh` and `python validate.py --compare`. All validation checks passed. The only stderr output was the same optional `cma.plot()` matplotlib warning, which does not affect training, optimization, or scoring.

## Pending Submission

The general evaluator now reports `cage_feature_range_violation` for every design in `scores.json`, matching the constraint metric already present in `reference.json` and in the train/test slice evaluators. A CPU test job is being submitted to rerun the packaged reproduction and validation after this evaluator fix and milestone downgrade.
