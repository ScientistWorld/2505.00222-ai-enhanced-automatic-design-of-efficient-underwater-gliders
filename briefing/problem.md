# Problem Definition

Design an autonomous underwater glider hull and operating angle of attack that maximizes hydrodynamic efficiency. Efficiency is measured by the nondimensional lift-to-drag ratio:

`eta = c_l / c_d`

where `c_l` is the lift coefficient and `c_d` is the drag coefficient for the candidate hull at the selected angle of attack.

The reusable benchmark represents each hull by a fixed low-dimensional vector of normalized shape parameters. The evaluation problem is to output a valid shape vector and an angle of attack in degrees. The design must be evaluated by the same hydrodynamic oracle used by the benchmark, and compared against a torpedo-like glider baseline under the same procedure.

Success requires improving lift-to-drag ratio while also reducing the implied energy per horizontal distance and maintaining a shallow glide trajectory. Invalid designs, out-of-range cage coordinates, or designs that only exploit a prediction model without improving under the independent evaluator do not solve the problem.
