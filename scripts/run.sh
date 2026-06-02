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

bash scripts/reproduce.sh
python validate.py --compare
