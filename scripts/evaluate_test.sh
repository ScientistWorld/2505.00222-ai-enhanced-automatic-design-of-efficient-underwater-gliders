#!/bin/bash
# Evaluate method outputs on the held-out fluid instances (test slice).
#
# Runs with no arguments: enumerates every outputs/*/optimization_results.json
# artifact and scores it against ground truth that exists only in eval/test/.

set -e

cd /home/user

mkdir -p scoring

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

python eval/test/evaluate.py --output scoring/scores_test.json "$@"
