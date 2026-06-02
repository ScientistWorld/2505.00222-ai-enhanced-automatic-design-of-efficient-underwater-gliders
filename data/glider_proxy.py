"""Problem data and lightweight hydrodynamic oracle for glider design.

The paper uses manually curated deformation-cage parameters and OpenFOAM CFD
labels that are not released. This module provides a deterministic substitute
problem with the same inputs and outputs: low-dimensional cage parameters plus
angle of attack map to drag and lift coefficients. It is intentionally placed
under data/ so both baselines and evaluation can use it without importing the
paper method implementation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


FEATURE_NAMES = [
    "span",
    "sweep",
    "camber",
    "thickness",
    "tail_area",
    "nose_bluntness",
    "ventral_fin",
    "lateral_symmetry",
]

ANGLE_GRID_DEG = np.array([-30.0, -15.0, 0.0, 15.0, 30.0], dtype=np.float32)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def base_shape_library() -> tuple[np.ndarray, list[str]]:
    """Return 20 normalized base cage parameter vectors.

    Values are hand-authored proxies for the paper's base shapes: torpedo,
    marine animals, rays, winged vehicles, and hybrids. Each row is in [0, 1]
    and represents offsets/handle settings of a reduced-order cage.
    """

    names = [
        "torpedo",
        "slocum_like",
        "seaglider_like",
        "manta_ray",
        "dolphin",
        "shark",
        "whale",
        "seal",
        "flying_wing",
        "delta_wing",
        "double_wing",
        "four_wing",
        "thin_ray",
        "wide_tail",
        "long_nose",
        "blunt_nose",
        "high_camber",
        "low_camber",
        "ventral_fin",
        "symmetric_plate",
    ]
    shapes = np.array(
        [
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
        ],
        dtype=np.float32,
    )
    return shapes, names


def torpedo_shape() -> np.ndarray:
    shapes, _ = base_shape_library()
    return shapes[0].copy()


def average_base_shape() -> np.ndarray:
    shapes, _ = base_shape_library()
    return shapes.mean(axis=0)


def interpolate_dataset(morphs_per_pair: int = 3) -> np.ndarray:
    """Interpolate base cage vectors, matching the paper's data expansion."""

    bases, _ = base_shape_library()
    rows = [bases]
    n = len(bases)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(1, morphs_per_pair + 1):
                t = k / (morphs_per_pair + 1)
                rows.append(((1.0 - t) * bases[i] + t * bases[j])[None, :])
    return np.concatenate(rows, axis=0).astype(np.float32)


def hydrodynamic_coefficients(shape: np.ndarray, aoa_deg: float | np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic CFD substitute returning (cd, cl).

    The formula encodes standard qualitative dependencies: cambered wide lifting
    surfaces increase lift, excessive thickness/bluntness/fin area increase drag,
    and each geometry has an AoA-dependent lift peak and stall penalty. It is
    not a replacement algorithm; it is the unavailable CFD label source.
    """

    x = np.asarray(shape, dtype=np.float32)
    a = np.asarray(aoa_deg, dtype=np.float32)
    aoa = np.deg2rad(a)

    span, sweep, camber, thickness, tail, blunt, fin, sym = np.moveaxis(x, -1, 0)
    aspect = 1.0 + 5.5 * span / (0.55 + thickness)
    lift_slope = (1.6 + 0.42 * aspect + 1.25 * tail + 0.55 * fin) * (0.82 + 0.18 * sym)
    zero_lift = np.deg2rad(-7.0 * camber + 1.5 * (blunt - 0.15))
    effective = aoa - zero_lift
    stall = 1.0 / (1.0 + np.exp((np.abs(np.rad2deg(effective)) - (18.0 + 12.0 * sweep)) / 3.2))
    cl = lift_slope * np.sin(effective) * np.cos(effective) * (0.45 + 0.55 * stall)
    cl += 0.20 * camber + 0.06 * fin - 0.04 * (1.0 - sym)

    wetted = 0.045 + 0.10 * thickness + 0.08 * blunt + 0.025 * fin
    induced = (cl * cl) / (math.pi * np.maximum(aspect, 0.5) * (0.70 + 0.22 * sym))
    separation = 0.018 * np.maximum(np.abs(np.rad2deg(effective)) - (14.0 + 10.0 * sweep), 0.0) ** 1.35 / 10.0
    cd = wetted + induced + separation + 0.018 * (1.0 - sym) + 0.010 * np.maximum(span - 0.86, 0.0) ** 2
    return np.asarray(np.maximum(cd, 1e-4), dtype=np.float32), np.asarray(np.maximum(cl, 0.0), dtype=np.float32)


def sample_training_table(morphs_per_pair: int = 3) -> tuple[np.ndarray, np.ndarray]:
    shapes = interpolate_dataset(morphs_per_pair)
    xs = []
    ys = []
    for shape in shapes:
        for angle in ANGLE_GRID_DEG:
            cd, cl = hydrodynamic_coefficients(shape, float(angle))
            xs.append(np.concatenate([shape, [angle / 30.0]], dtype=np.float32))
            ys.append(np.array([cd.item(), cl.item()], dtype=np.float32))
    return np.stack(xs), np.stack(ys)


def lift_to_drag(cd: float, cl: float) -> float:
    return float(cl / max(cd, 1e-8))


def trajectory_angle_deg(eta: float) -> float:
    return float(np.rad2deg(np.arctan(1.0 / max(eta, 1e-8))))


def write_design(path: str | Path, name: str, shape: np.ndarray, aoa_deg: float, extra: dict | None = None) -> None:
    cd, cl = hydrodynamic_coefficients(shape, aoa_deg)
    eta = lift_to_drag(float(cd), float(cl))
    payload = {
        "name": name,
        "shape": np.asarray(shape, dtype=float).tolist(),
        "aoa_deg": float(aoa_deg),
        "oracle_cd": float(cd),
        "oracle_cl": float(cl),
        "oracle_lift_to_drag": eta,
        "oracle_energy_per_distance_relative": float(1.0 / max(eta, 1e-8)),
        "oracle_trajectory_angle_deg": trajectory_angle_deg(eta),
    }
    if extra:
        payload.update(extra)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
