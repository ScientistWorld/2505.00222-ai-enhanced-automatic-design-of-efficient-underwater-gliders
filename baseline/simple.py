#!/usr/bin/env python3
"""Simple design baselines that use only the public data.

* ``torpedo``          - the conventional torpedo hull at its best labelled angle.
* ``average``          - the average of the base hulls (the search's starting
                         point) with no optimisation.
* ``best_in_dataset``  - exhaustive lookup over the labelled dataset: the best
                         labelled hull at each requested angle (linear in angle
                         between label angles) and the best labelled
                         (hull, angle) pair for the co-design; coefficient
                         predictions from the nearest labelled hull.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from data.glider_proxy import (
    DESIGN_ANGLES, LABEL_AOA_DEG, TORPEDO_INDEX, all_instance_ids, average_weights,
    dataset_shapes, dataset_weights, instance_design, load_labels, load_queries,
    one_hot_weights, write_artifact,
)

LABELS = np.asarray(LABEL_AOA_DEG)


def eta_table(instance_id: str) -> np.ndarray:
    """(n_shapes, n_label_angles) labelled lift-to-drag."""

    lab = load_labels(instance_id)
    n = int(lab["shape_id"].max()) + 1
    table = np.zeros((n, len(LABELS)))
    cols = np.searchsorted(LABELS, lab["aoa_deg"])
    table[lab["shape_id"], cols] = lab["cl"] / np.maximum(lab["cd"], 1e-8)
    return table


def interp_columns(table: np.ndarray, angle: float) -> np.ndarray:
    return np.array([np.interp(angle, LABELS, row) for row in table])


def predict_nearest(instance_id: str) -> np.ndarray:
    lab = load_labels(instance_id)
    q = load_queries(instance_id)
    shapes = dataset_shapes()
    n = len(shapes)
    cd = np.zeros((n, len(LABELS)))
    cl = np.zeros((n, len(LABELS)))
    cols = np.searchsorted(LABELS, lab["aoa_deg"])
    cd[lab["shape_id"], cols] = lab["cd"]
    cl[lab["shape_id"], cols] = lab["cl"]
    out = []
    for s, a in zip(q["shape"], q["aoa_deg"]):
        i = int(np.argmin(((shapes - s) ** 2).sum(axis=1)))
        out.append([max(np.interp(a, LABELS, cd[i]), 1e-6), np.interp(a, LABELS, cl[i])])
    return np.asarray(out)


def design(mode: str, instance_id: str) -> dict:
    if mode == "torpedo":
        table = eta_table(instance_id)
        w = one_hot_weights(TORPEDO_INDEX)
        aoa = float(LABELS[int(np.argmax(table[TORPEDO_INDEX]))])
        return instance_design(w, aoa, {lab: w for lab in DESIGN_ANGLES})
    if mode == "average":
        table = eta_table(instance_id)
        w = average_weights()
        aoa = float(LABELS[int(np.argmax(table.mean(axis=0)))])
        return instance_design(w, aoa, {lab: w for lab in DESIGN_ANGLES})
    if mode == "best_in_dataset":
        table = eta_table(instance_id)
        weights = dataset_weights()
        i, j = np.unravel_index(int(np.argmax(table)), table.shape)
        angle_w = {lab: weights[int(np.argmax(interp_columns(table, float(lab))))] for lab in DESIGN_ANGLES}
        return instance_design(weights[i], float(LABELS[j]), angle_w, predict_nearest(instance_id))
    raise ValueError(f"unknown baseline {mode!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["torpedo", "average", "best_in_dataset"], required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()
    out = Path(args.output_dir or f"outputs/{args.mode}")
    name = args.name or f"{args.mode}_glider"
    write_artifact(out / "optimization_results.json", name,
                   {iid: design(args.mode, iid) for iid in all_instance_ids()})


if __name__ == "__main__":
    main()
