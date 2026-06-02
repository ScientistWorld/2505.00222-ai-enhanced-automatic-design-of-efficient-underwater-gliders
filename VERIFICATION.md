# Verification

Latest completed full reproduction smoke job: `6b0aae30-c2a` with exit code 0.
Latest completed train/test slice job: `25d3a54e-c15` with exit code 0.

Commands executed by the job:

```bash
bash scripts/reproduce.sh
python validate.py --compare
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
```

Final reproduced scores are written by `scripts/evaluate.sh` to `scoring/scores.json`; train/test diagnostics are written to `scoring/scores_train.json` and `scoring/scores_test.json`. `python validate.py --compare` passes.

The evaluator reports direct uncalibrated hydrodynamic-oracle scores from method artifacts. This avoids fitting local results to paper values; paper pool-test numbers remain only in `scoring/reference.json`.

Summary:
- `pool_efficiency`: optimized lift-to-drag 9.708 versus torpedo baseline 0.982, for a gain of 9.884.
- `surrogate_validation`: surrogate eta error 6.711 percent with oracle eta 9.708 and surrogate eta 9.057.
- `angle_sweep_efficiency`: 9-degree gain 9.884 and 30-degree gain 6.351 over the torpedo baseline.
- `scores_train.json` and `scores_test.json` verify that the same method artifacts score on visible and held-out operating-angle slices.

Milestone reached: `core_claim_plus`. The physical secondary claims are not claimed because the paper's real cage-fitted meshes, OpenFOAM data, wind-tunnel measurements, and pool telemetry are unavailable.
