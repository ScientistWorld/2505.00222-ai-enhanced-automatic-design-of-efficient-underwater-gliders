# Research Direction

## Research Problem
This benchmark studies automated hydrodynamic co-design of underwater glider hull shape and angle of attack. The goal is to find valid low-dimensional hull designs that improve lift-to-drag efficiency over conventional torpedo-like designs.

## Core Contribution
The paper's contribution is an efficient design loop for glider geometry: low-dimensional cage-based shape representation, learned fluid surrogate, and optimization of shape/control for lift-to-drag ratio. Future improvements should work within this automated co-design setting.

## Approach Scope
A scientist may improve the surrogate model, the sampling strategy, the optimizer, the way uncertainty is handled, or the way the existing shape library is explored. The work should still produce glider shape parameters and an angle of attack evaluated by the benchmark.

## Out of Bounds
Switching to a different task, using external hydrodynamic labels for scored experiments, bypassing design optimization by hand-writing the answer, or modifying the evaluator to favor a method is out of bounds. Replacing the glider-design problem with a generic regression or black-box score-fitting task is also out of bounds.
