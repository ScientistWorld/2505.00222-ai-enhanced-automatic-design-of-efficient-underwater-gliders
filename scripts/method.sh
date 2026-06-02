#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

epochs="${EPOCHS:-200}"
generations="${GENERATIONS:-80}"
population="${POPULATION:-24}"
angles="${ANGLES:-9,30}"

mkdir -p checkpoints outputs/proposed
python -m method.train_surrogate \
  --checkpoint checkpoints/fluid_surrogate.pt \
  --epochs "$epochs" \
  --batch-size 128 \
  --lr 0.1 \
  --morphs-per-pair 3

python -m method.optimize \
  --checkpoint checkpoints/fluid_surrogate.pt \
  --output-dir outputs/proposed \
  --angles "$angles" \
  --generations "$generations" \
  --population "$population"

if [ ! -e outputs/torpedo/optimization_results.json ]; then
  python -m baseline.torpedo --output-dir outputs/torpedo
fi

bash scripts/evaluate.sh
