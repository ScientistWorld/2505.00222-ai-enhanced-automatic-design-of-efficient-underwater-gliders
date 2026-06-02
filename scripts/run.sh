#!/bin/bash
# Job script submitted via action.yaml.

set -e

cd /home/user

bash scripts/evaluate.sh
python validate.py --compare
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
python validate.py --compare
