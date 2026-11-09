# Research Direction

## Research Problem
Automated hydrodynamic co-design of underwater-glider hull shape and angle of attack under a fixed simulation budget. Each fluid instance provides a labelled dataset of the paper's size. The goal is to turn that data into hulls with the best true lift-to-drag ratio, plus accurate predictions of efficiency for unseen hulls.

## Core Contribution
The paper's contribution is a data-driven design loop: a reduced-order shape space, a learned hydrodynamic model, and global search inside the convex hull of known shapes. The loop beats conventional torpedo designs by a wide margin.

## Approach Scope
In scope: better predictive models of the fluid response (architecture, training, ensembles, uncertainty), better search and selection inside the design domain, how much to trust predictions away from the labelled data, and how to co-select the operating angle. Every design must come from an instance's own published data.

## Out of Bounds
- Using the evaluator's ground-truth code or its functional form as a label source, model or optimisation target.
- Adding simulation labels.
- Hand-writing designs per instance.
- Editing the evaluator.
- Swapping the glider-design task for a different one.
