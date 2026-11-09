#!/usr/bin/env python3
"""Surrogate-based CMA-ES shape optimisation inside the base-shape convex hull.

For each angle of attack on the design grid the search starts from the average
of the training shapes (uniform convex weights), runs CMA-ES on softmax logits
so every candidate is a convex combination of the base hulls, and is repeated
several times; the best design per angle is the one with the highest surrogate
lift-to-drag ratio. The co-designed (shape, angle) pair is the best of those.
No ground-truth evaluation is used anywhere in the search or the selection.
"""

from __future__ import annotations

import cma
import numpy as np

from data.glider_proxy import base_shape_library
from method.train_surrogate import Predictor, features


def softmax_rows(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def optimise_angle(predictor: Predictor, angle: float, seed: int, generations: int = 80,
                   population: int = 24, sigma0: float = 0.85) -> tuple[np.ndarray, float]:
    bases, _ = base_shape_library()
    es = cma.CMAEvolutionStrategy(
        np.zeros(len(bases)),
        sigma0,
        {"seed": int(seed), "popsize": population, "maxiter": generations,
         "verbose": -9, "verb_disp": 0, "verb_log": 0},
    )
    while not es.stop():
        sols = es.ask()
        w = softmax_rows(np.asarray(sols))
        eta = predictor.lift_to_drag(features(w @ bases, angle))
        es.tell(sols, (-eta).tolist())
    w = softmax_rows(np.asarray(es.result.xbest)[None, :])[0]
    pred = float(predictor.lift_to_drag(features((w @ bases)[None, :], angle))[0])
    return w, pred


def design_instance(predictor: Predictor, angles: list[float], design_angles: list[str],
                    restarts: int = 3, generations: int = 80, population: int = 24,
                    seed: int = 0) -> dict:
    per_angle = {}
    for a_idx, angle in enumerate(angles):
        best = None
        for r in range(restarts):
            cma_seed = 1 + seed * 100003 + a_idx * 101 + r
            w, pred = optimise_angle(predictor, angle, cma_seed, generations, population)
            if best is None or pred > best[1]:
                best = (w, pred)
        per_angle[angle] = best
    pool_angle = max(per_angle, key=lambda a: per_angle[a][1])
    missing = [lab for lab in design_angles if float(lab) not in per_angle]
    if missing:
        raise ValueError(f"design angles {missing} are not on the optimisation grid {angles}")
    return {
        "pool_weights": per_angle[pool_angle][0],
        "pool_aoa_deg": pool_angle,
        "angle_weights": {lab: per_angle[float(lab)][0] for lab in design_angles},
        "predicted_eta": {f"{a:g}": p for a, (_, p) in per_angle.items()},
    }
