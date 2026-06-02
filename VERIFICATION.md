# Verification

Final verified job: `1b4dcf49-45e` with exit code 0.

Commands executed by the job:

```bash
bash scripts/reproduce.sh
```

Validation command run after completion:

```bash
python validate.py --compare
```

Final reproduced scores are in `scoring/scores.json`.

Summary:
- `pool_efficiency`: optimized lift-to-drag 9.708 versus torpedo baseline 0.982.
- `surrogate_validation`: surrogate eta error 6.711 percent.
- `angle_sweep_efficiency`: 9-degree eta 9.708 and 30-degree eta 6.238.

Milestone reached: `core_claim_plus`.
