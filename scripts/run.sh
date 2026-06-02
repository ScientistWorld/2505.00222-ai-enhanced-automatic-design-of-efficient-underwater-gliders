#!/bin/bash
# Job script submitted via the end-of-turn YAML block.
#
# This runs inside the compute container with:
#   - Your workspace mounted at /home/user
#   - GPU(s) available
#   - No internet access
#
# Make sure all data, code, and dependencies are already in the
# workspace or baked into the container before submitting.

set -e

cd /home/user

export EPOCHS="${EPOCHS:-200}"
export GENERATIONS="${GENERATIONS:-80}"
export POPULATION="${POPULATION:-24}"
export ANGLES="${ANGLES:-9,30}"

rm -rf tmp/audit_baseline_eval
mkdir -p tmp/audit_baseline_eval
python -m baseline.torpedo --output-dir tmp/audit_baseline_eval/torpedo
bash scripts/evaluate.sh \
  --baseline tmp/audit_baseline_eval/torpedo/optimization_results.json \
  --proposed tmp/audit_baseline_eval/missing_proposed.json \
  --output tmp/audit_baseline_eval/scores.json
python - <<'PY'
import json
from pathlib import Path

scores = json.loads(Path("tmp/audit_baseline_eval/scores.json").read_text())
experiments = scores["experiments"]
assert set(experiments) == {"pool_efficiency"}, experiments
results = experiments["pool_efficiency"]["results"]
assert set(results) == {"torpedo_baseline"}, results
assert results["torpedo_baseline"]["efficiency_gain_over_torpedo"] == 1.0
PY

bash scripts/reproduce.sh
python validate.py --compare
