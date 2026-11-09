#!/bin/bash
# Run a simple baseline that uses only the public data.
#
# Usage:
#   bash scripts/baseline.sh best_in_dataset   # exhaustive lookup over the labelled dataset
#   bash scripts/baseline.sh average           # average base hull, no search
#   bash scripts/baseline.sh torpedo           # conventional torpedo hull
#
# The artifact goes to outputs/<name>/ and every method on disk is rescored.

set -e

cd /home/user

export PYTHONPATH="/home/user:${PYTHONPATH:-}"

name="${1:-best_in_dataset}"
case "$name" in
  torpedo|average|best_in_dataset)
    python -m baseline.simple --mode "$name" --output-dir "outputs/$name"
    ;;
  *)
    echo "Unknown baseline: $name (choose torpedo, average, best_in_dataset)" >&2
    exit 2
    ;;
esac

bash scripts/evaluate.sh
