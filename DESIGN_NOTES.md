# Train/Test Evaluation Design Notes

## Checked

- Read `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh` side by side. The train wrapper calls `eval/train/evaluate.py` and writes `scoring/scores_train.json`; the test wrapper calls `eval/test/evaluate.py` and writes `scoring/scores_test.json`.
- Checked for hardcoded method defaults. Both slice evaluators discover `outputs/*/optimization_results.json` artifacts unless explicit `--proposed` / `--baseline` paths are supplied.
- Checked eval independence from `method/`. The slice evaluators read method output artifacts and import only neutral `data.glider_proxy` code, not `method/`.
- Checked for score stubs. No `scoring/scores_train.json` or `scoring/scores_test.json` files were present.
- Ran `bash -n` on both train/test shell wrappers.

## Changed

- Added `cage_feature_range_violation` to `eval/train/` and `eval/test/` for `pool_efficiency` and `angle_sweep_efficiency`. This penalizes submitted cage vectors that leave the feature envelope of the base shape library, closing a shortcut where an agent could chase oracle lift-to-drag with out-of-domain shape parameters.
- Changed pooled train scoring from a single visible 9-degree condition to the visible paper conditions `(9, 30)` and changed pooled test scoring to held-out nearby conditions `(12, 24)`. This makes the train/test gap more informative for single-angle overfitting while keeping difficulty calibrated.
- Changed angle-sweep gain normalization to use the torpedo baseline at the same evaluated angle rather than the pooled baseline. This fixes an angle-mismatch scoring artifact.
- Added required metric descriptions throughout `scoring/reference.json`.
- Reweighted experiments from `0.6/0.2/0.2` to `0.5/0.3/0.2`, giving the multi-angle generalization slice more influence while keeping pooled efficiency primary.

## Runtime Concerns For Next Iteration

- The new cage-range metric is a feature-envelope constraint, not a full convex-hull projection. It catches out-of-range cage shortcuts without adding a dependency, but a shape can still be inside each feature range while outside the exact convex hull.
- The held-out test slice still reads `scoring/scores_train.json` if present only to verify that every train-scored method key is also test-scored. If final infrastructure runs test without train scores, this check becomes a no-op.
- The next runner should confirm generated train/test scores include `cage_feature_range_violation` for both pool and angle experiments and that existing reproduced shapes do not saturate every metric.
