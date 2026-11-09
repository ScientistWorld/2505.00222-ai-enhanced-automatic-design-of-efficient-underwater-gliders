#!/bin/bash
# Evaluate method outputs on the public development fluid instances (train slice).
#
# Enumerates every outputs/*/optimization_results.json artifact; no method name
# is assumed. Pass --outputs-dir to score artifacts elsewhere.

set -e

cd /home/user

mkdir -p scoring

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

python eval/train/evaluate.py --output scoring/scores_train.json "$@"
