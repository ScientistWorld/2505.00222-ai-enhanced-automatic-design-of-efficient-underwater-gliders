#!/bin/bash
# Download all data and models needed for this environment.
#
# Estimated total download size: 0 GB
# Estimated disk usage after extraction: 0 GB
#
# Nothing is fetched. The paper's meshes, cage fits and OpenFOAM labels were
# never released; this benchmark's base-hull library and per-instance labelled
# datasets are small tracked files under data/ (data/glider_proxy.py,
# data/instances/), and no pretrained weights are used. The script only
# creates the standard downloads directory so fresh clones have the layout.

set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p data/downloads
test -f data/instances/index.json || { echo "data/instances/ missing from checkout" >&2; exit 1; }
echo "No external downloads required."
