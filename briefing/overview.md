# Overview

This workspace reproduces the core computational claim of *AI-Enhanced Automatic Design of Efficient Underwater Gliders*: a reduced-order shape representation, a neural hydrodynamic surrogate trained on a fixed simulation budget, and CMA-ES together discover glider hulls with far better lift-to-drag efficiency than a manually designed torpedo-like baseline.

The unreleased CFD and physical assets are replaced by synthetic fluid instances whose ground truth is hidden from the method: each instance exposes only a labelled dataset of the paper's size, and designs are scored by the evaluator's ground truth on held-out instances.
