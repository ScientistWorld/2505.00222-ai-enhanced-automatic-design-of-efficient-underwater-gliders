#!/bin/bash
# Evaluation script — the standard way to evaluate work in this environment.
#
# Self-contained: uses only code in eval/ (never method/). Scores every
# outputs/<method>/optimization_results.json on the public development fluid
# instances and writes scoring/scores.json (same content as the train slice).
#
# Usage:
#   bash scripts/evaluate.sh                       # score every method on disk
#   bash scripts/evaluate.sh --outputs-dir DIR     # score artifacts under DIR

set -e

cd /home/user

mkdir -p scoring

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

python eval/train/evaluate.py --output scoring/scores.json "$@"
