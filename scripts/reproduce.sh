#!/bin/bash
# Reproduce the reference end-to-end: fetch nothing (all data is tracked), run
# the paper's method on every fluid instance, then score the development
# (train) and held-out (test) slices.

set -e

cd /home/user

bash scripts/download.sh
rm -rf outputs/proposed
bash scripts/method.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
