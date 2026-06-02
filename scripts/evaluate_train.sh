#!/bin/bash
# Evaluate method outputs on the visible train slice.
#
# Mirrors scripts/evaluate.sh: pass --proposed, --baseline, --output, or other
# evaluator flags through to the slice evaluator. With no --proposed flag, all
# outputs/*/optimization_results.json method artifacts are enumerated.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate.py --output scoring/scores_train.json "$@"
