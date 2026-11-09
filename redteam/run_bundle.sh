#!/bin/bash
set -euo pipefail
cd /home/user
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH="/home/user:${PYTHONPATH:-}"
python redteam/harness.py all
python redteam/summarize.py
