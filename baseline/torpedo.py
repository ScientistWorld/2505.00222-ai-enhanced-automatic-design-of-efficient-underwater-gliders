#!/usr/bin/env python3
"""Torpedo-shaped baseline used by the paper for comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from data.glider_proxy import ANGLE_GRID_DEG, hydrodynamic_coefficients, lift_to_drag, torpedo_shape, write_design


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/torpedo")
    args = parser.parse_args()

    shape = torpedo_shape()
    candidates = []
    for angle in np.linspace(float(ANGLE_GRID_DEG.min()), float(ANGLE_GRID_DEG.max()), 25):
        cd, cl = hydrodynamic_coefficients(shape, float(angle))
        candidates.append((lift_to_drag(float(cd), float(cl)), float(angle)))
    best_eta, best_angle = max(candidates, key=lambda item: item[0])
    write_design(
        Path(args.output_dir) / "optimization_results.json",
        "torpedo",
        shape,
        best_angle,
        {"selection": "best_angle_for_fixed_torpedo", "searched_eta": best_eta},
    )


if __name__ == "__main__":
    main()
