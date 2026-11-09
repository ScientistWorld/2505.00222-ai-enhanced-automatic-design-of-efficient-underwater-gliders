# Problem Definition

Design underwater-glider hulls, and the angle of attack they fly at, that maximise hydrodynamic efficiency. Efficiency is the lift-to-drag ratio

`eta = c_l / c_d`

of the hull at its operating angle of attack. The work the buoyancy engine spends per horizontal distance is proportional to `c_d / c_l`, and the glide-path angle is `atan(c_d / c_l)`, so a higher `eta` means less energy per distance and a shallower glide.

## Design domain

A hull is described by 8 normalised descriptors (span, sweep, camber, thickness, tail area, nose bluntness, ventral fin, lateral symmetry). The admissible designs are the convex hull of a fixed library of 20 base hulls (`data/glider_proxy.py`). A design is therefore submitted as 20 non-negative convex weights over the library, summing to 1. The angle of attack is limited to the actuator range of -30 to +30 degrees.

## What is known about the fluid

Hydrodynamic coefficients come from an expensive simulator that you cannot call. Each *fluid instance* is a different flow response over the same hull library. For every instance you get a fixed labelled dataset (`data/instances/<id>/labels.csv`): `c_d` and `c_l` for every base hull and 10 evenly spaced morphs between every pair of base hulls (1,920 hulls), each at -30, -15, 0, 15 and 30 degrees. That is the whole simulation budget. The labels come from a simulation: every published coefficient carries an independent error of a few percent. Designs and predictions are scored against the error-free response.

There are two kinds of instance (`data/instances/index.json`):

- **development instances** (`dev_*`), scored by `scripts/evaluate_train.sh` while you work;
- **held-out instances** (`heldout_*`), whose labelled datasets are public but which are scored only by the hidden test.

Your method has to produce designs for every listed instance from that instance's data.

## Tasks per instance

1. **Co-design**: one hull and one angle of attack with the highest efficiency.
2. **Fixed operating angles**: one hull for 9 degrees and one for 30 degrees.
3. **Prediction**: predicted `c_d` and `c_l` for 400 public query (hull, angle) pairs (`queries.json`). Their true values are hidden.

A design counts only through the evaluator's ground truth. Designs outside the convex hull, angles outside the actuator range, and non-finite or physically impossible values do not solve the problem.
