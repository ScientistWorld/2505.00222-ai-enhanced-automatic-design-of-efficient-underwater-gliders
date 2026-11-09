# Experiment Overview

All experiments are averaged over the fluid instances of a slice: two public development instances (train) and six held-out instances (hidden test). The method sees only each instance's labelled dataset, whose labels carry simulation error. The error-free ground truth stays inside the evaluator.

## pool_efficiency (weight 0.5)
Can a hull and operating angle chosen jointly beat a conventional torpedo-shaped glider on efficiency? This is the paper's central practical claim: automated design finds gliders that need less energy per distance than the standard design. The design is scored at the angle the submitter chose. The torpedo is scored at its own best angle. Both evaluations happen inside the evaluator.

## angle_sweep_efficiency (weight 0.35)
Are efficient hulls found at each of the two operating angles the paper fabricated (9° and 30°)? The paper's optima differ by angle, so this tests designing for a prescribed control setting, not only the easiest one.

## surrogate_validation (weight 0.15)
How accurately does the submission predict hydrodynamic efficiency for hulls and angles it was not given labels for? The paper validates its predictions against measurements and reports 4.5% lift-to-drag error. Here the evaluator's ground truth plays that role on public query inputs.

## Constraint
Designs must stay in the convex hull of the base-hull library, and angles in the actuator range. Any constraint violation or impossible value fails the whole submission, and every metric then takes its worst value.
