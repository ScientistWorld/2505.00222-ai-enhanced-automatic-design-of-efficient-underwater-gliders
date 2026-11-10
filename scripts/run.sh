#!/bin/bash
# Job script submitted via action.yaml: reproduce the reference end to end
# (paper's method on every published instance, then the development and
# held-out evaluations) and validate the workspace.
#
# The hardening study that produced HARDENING.md is `python hardening/harness.py all`
# followed by `python hardening/summarize.py`.

set -e

cd /home/user
export PYTHONPATH=/home/user

bash scripts/reproduce.sh
python validate.py
