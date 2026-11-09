#!/bin/bash
# Job script submitted via action.yaml.

set -e

cd /home/user

bash redteam/run_bundle.sh
