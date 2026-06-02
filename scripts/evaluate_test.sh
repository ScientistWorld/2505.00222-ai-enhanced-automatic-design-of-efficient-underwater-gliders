#!/bin/bash
# Evaluate method outputs on the held-out test slice.
#
# Mirrors scripts/evaluate.sh: pass --proposed, --baseline, --output, or other
# evaluator flags through to the slice evaluator. With no --proposed flag, all
# outputs/*/optimization_results.json method artifacts are enumerated.

set -e

cd /home/user

mkdir -p scoring

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

python eval/test/evaluate.py --output scoring/scores_test.json "$@"
