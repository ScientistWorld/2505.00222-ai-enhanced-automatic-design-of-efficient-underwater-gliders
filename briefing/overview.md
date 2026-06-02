# Overview

This workspace reproduces the core computational claim of *AI-Enhanced Automatic Design of Efficient Underwater Gliders*: a reduced-order shape representation plus a neural hydrodynamic surrogate and CMA-ES can discover glider hulls with better lift-to-drag efficiency than a manually designed torpedo-like baseline.

The unreleased physical and CFD assets are replaced by a deterministic benchmark oracle, while the algorithmic pipeline remains the paper's: shared cage parameters, interpolated shapes, 4-layer tanh/batchnorm surrogate, and convex-hull-constrained CMA-ES shape optimization across angle-of-attack settings.
