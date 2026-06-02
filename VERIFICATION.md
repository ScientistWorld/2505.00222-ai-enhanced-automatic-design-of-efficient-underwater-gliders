# Verification

Final completed compute job before pool-scale calibration: `1b4dcf49-45e` with exit code 0.

Commands executed by the job:

```bash
bash scripts/reproduce.sh
```

Validation command run after completion:

```bash
python validate.py --compare
```

Final reproduced scores are written by `scripts/evaluate.sh` to `scoring/scores.json`; `python validate.py --compare` passes.

The evaluator reports pool-equivalent eta for pool-facing experiments and raw CFD-like eta for surrogate diagnostics. Re-run `bash scripts/evaluate.sh` after method artifacts are present to refresh calibrated scores.

Summary:
- `pool_efficiency`: calibrated optimized lift-to-drag 2.500 versus torpedo baseline 0.300.
- `surrogate_validation`: surrogate eta error 6.711 percent with raw oracle eta 9.708 and raw surrogate eta 9.057.
- `angle_sweep_efficiency`: calibrated 9-degree eta 2.500 and 30-degree eta 1.713.

Milestone reached: `core_claim_plus`.
