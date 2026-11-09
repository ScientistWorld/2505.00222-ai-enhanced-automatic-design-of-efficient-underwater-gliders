#!/bin/bash
# Job script submitted via action.yaml.
#
# Hardening job: honest variants, baselines and shortcuts through the
# unmodified no-argument hidden test (hardening/harness.py, resumable), the
# rank summary, then the end-to-end reference reproduction that produces the
# committed score files, validation, and a difficulty calibration on
# throwaway instance families.

set -e

cd /home/user
export PYTHONPATH=/home/user

python hardening/harness.py all
python hardening/summarize.py

bash scripts/reproduce.sh
python - <<'PY'
import json
a = json.load(open("outputs/proposed/optimization_results.json"))["instances"]
b = json.load(open("hardening/cases/reference/artifact/optimization_results.json"))["instances"]
print("reproduce.sh artifact identical to the harness reference:", a == b)
PY
python validate.py || echo "VALIDATE FAILED"

python hardening/calibrate.py || echo "calibration failed (non-fatal)"
