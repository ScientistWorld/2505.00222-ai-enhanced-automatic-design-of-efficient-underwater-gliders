#!/bin/bash
# Run the paper's method (neural fluid surrogate + convex-hull CMA-ES) on every
# published fluid instance and score it on the development instances.
#
# Usage:
#   bash scripts/method.sh                 # paper settings, seed 0
#   SEED=1 bash scripts/method.sh          # another seed
#   bash scripts/method.sh --ensemble 5    # extra flags go to method.pipeline

set -e

cd /home/user

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

mkdir -p checkpoints outputs/proposed
python -m method.pipeline \
  --output-dir outputs/proposed \
  --name ai_enhanced_glider \
  --seed "${SEED:-0}" \
  --epochs 200 --lr 0.1 --batch-size 128 --warmup 10 \
  --angles 0,3,6,9,12,15,18,21,24,27,30 --restarts 3 \
  --generations 80 --population 24 \
  "$@"

bash scripts/evaluate.sh
