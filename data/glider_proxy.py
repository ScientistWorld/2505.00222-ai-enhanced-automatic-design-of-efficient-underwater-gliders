"""Public problem data for the glider-design benchmark.

What a method may use:

* the 20-hull base library (8 normalised hull descriptors each); the design
  domain is the convex hull of these vectors, so designs are submitted as
  convex weights over the library;
* for every fluid instance listed in ``data/instances/index.json``, a labelled
  dataset (``labels.csv``): drag and lift coefficients of every base hull and
  pairwise morph at the label angles of attack -- the analogue of a fixed CFD
  budget;
* query inputs (``queries.json``) whose coefficients a method may predict.

The hydrodynamic ground truth itself is not part of the public data. Scores
come from ``scripts/evaluate_train.sh`` (development instances) and the held-out
test (held-out instances).
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent
# GLIDER_INSTANCE_DIR lets experiments point the loaders at another instance set.
INSTANCE_DIR = Path(os.environ.get("GLIDER_INSTANCE_DIR", DATA_DIR / "instances"))

FEATURE_NAMES = [
    "span", "sweep", "camber", "thickness", "tail_area", "nose_bluntness",
    "ventral_fin", "lateral_symmetry",
]
BASE_NAMES = [
    "torpedo", "slocum_like", "seaglider_like", "manta_ray", "dolphin", "shark",
    "whale", "seal", "flying_wing", "delta_wing", "double_wing", "four_wing",
    "thin_ray", "wide_tail", "long_nose", "blunt_nose", "high_camber",
    "low_camber", "ventral_fin", "symmetric_plate",
]
_BASE_SHAPES = [
    [0.10, 0.12, 0.05, 0.46, 0.08, 0.18, 0.03, 0.92],
    [0.16, 0.10, 0.08, 0.42, 0.16, 0.18, 0.05, 0.90],
    [0.22, 0.16, 0.10, 0.38, 0.22, 0.16, 0.08, 0.91],
    [0.82, 0.28, 0.24, 0.18, 0.20, 0.08, 0.10, 0.88],
    [0.34, 0.18, 0.17, 0.32, 0.34, 0.10, 0.08, 0.87],
    [0.42, 0.34, 0.14, 0.28, 0.38, 0.13, 0.12, 0.86],
    [0.30, 0.12, 0.11, 0.40, 0.30, 0.09, 0.05, 0.88],
    [0.40, 0.24, 0.20, 0.30, 0.22, 0.12, 0.20, 0.74],
    [0.68, 0.42, 0.17, 0.20, 0.20, 0.10, 0.07, 0.94],
    [0.74, 0.62, 0.14, 0.16, 0.14, 0.08, 0.05, 0.96],
    [0.72, 0.34, 0.28, 0.20, 0.36, 0.08, 0.10, 0.90],
    [0.78, 0.24, 0.28, 0.22, 0.44, 0.10, 0.28, 0.82],
    [0.92, 0.18, 0.20, 0.10, 0.18, 0.06, 0.05, 0.86],
    [0.46, 0.16, 0.12, 0.34, 0.52, 0.12, 0.18, 0.84],
    [0.28, 0.22, 0.08, 0.30, 0.20, 0.04, 0.05, 0.92],
    [0.24, 0.12, 0.10, 0.42, 0.18, 0.34, 0.04, 0.88],
    [0.58, 0.30, 0.34, 0.24, 0.28, 0.10, 0.18, 0.78],
    [0.56, 0.28, 0.06, 0.22, 0.20, 0.10, 0.05, 0.96],
    [0.44, 0.18, 0.16, 0.30, 0.28, 0.12, 0.42, 0.72],
    [0.62, 0.08, 0.04, 0.18, 0.10, 0.10, 0.04, 0.98],
]
TORPEDO_INDEX = 0
LABEL_AOA_DEG = (-30.0, -15.0, 0.0, 15.0, 30.0)
MORPHS_PER_PAIR = 10
AOA_RANGE_DEG = (-30.0, 30.0)
DESIGN_ANGLES = ("9", "30")


def base_shape_library() -> tuple[np.ndarray, list[str]]:
    return np.asarray(_BASE_SHAPES, dtype=np.float64), list(BASE_NAMES)


def average_weights() -> np.ndarray:
    return np.full(len(_BASE_SHAPES), 1.0 / len(_BASE_SHAPES))


def one_hot_weights(index: int) -> np.ndarray:
    w = np.zeros(len(_BASE_SHAPES))
    w[index] = 1.0
    return w


def mix(weights) -> np.ndarray:
    bases, _ = base_shape_library()
    return np.asarray(weights, dtype=np.float64) @ bases


def dataset_weights(morphs_per_pair: int = MORPHS_PER_PAIR) -> np.ndarray:
    """Convex weights of every labelled hull, in ``labels.csv`` shape_id order."""

    n = len(_BASE_SHAPES)
    rows = [one_hot_weights(i) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(1, morphs_per_pair + 1):
                t = k / (morphs_per_pair + 1)
                w = np.zeros(n)
                w[i], w[j] = 1.0 - t, t
                rows.append(w)
    return np.stack(rows)


def dataset_shapes(morphs_per_pair: int = MORPHS_PER_PAIR) -> np.ndarray:
    bases, _ = base_shape_library()
    return dataset_weights(morphs_per_pair) @ bases


def load_index() -> dict:
    return json.loads((INSTANCE_DIR / "index.json").read_text())


def all_instance_ids() -> list[str]:
    index = load_index()
    return list(index["development"]) + list(index["heldout"])


def load_labels(instance_id: str) -> dict:
    """Labelled dataset of one fluid instance as numpy arrays."""

    shapes = dataset_shapes()
    sid, aoa, cd, cl = [], [], [], []
    with open(INSTANCE_DIR / instance_id / "labels.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            sid.append(int(row["shape_id"]))
            aoa.append(float(row["aoa_deg"]))
            cd.append(float(row["cd"]))
            cl.append(float(row["cl"]))
    sid = np.asarray(sid)
    return {
        "shape_id": sid,
        "shape": shapes[sid],
        "aoa_deg": np.asarray(aoa),
        "cd": np.asarray(cd),
        "cl": np.asarray(cl),
    }


def load_queries(instance_id: str) -> dict:
    data = json.loads((INSTANCE_DIR / instance_id / "queries.json").read_text())
    q = data["queries"]
    weights = np.asarray([item["weights"] for item in q], dtype=np.float64)
    return {
        "weights": weights,
        "shape": mix(weights),
        "aoa_deg": np.asarray([item["aoa_deg"] for item in q], dtype=np.float64),
    }


def instance_design(pool_weights, pool_aoa_deg: float, angle_weights: dict, query_predictions=None) -> dict:
    """One instance entry of ``outputs/<method>/optimization_results.json``."""

    entry = {
        "pool_design": {"weights": [float(v) for v in pool_weights], "aoa_deg": float(pool_aoa_deg)},
        "angle_designs": {str(k): {"weights": [float(v) for v in w]} for k, w in angle_weights.items()},
    }
    if query_predictions is not None:
        entry["query_predictions"] = [[float(a), float(b)] for a, b in np.asarray(query_predictions)]
    return entry


def write_artifact(path: str | Path, name: str, instances: dict, extra: dict | None = None) -> None:
    payload = {"name": name, "instances": instances}
    if extra:
        payload.update(extra)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n")
