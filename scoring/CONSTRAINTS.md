# Scientist Constraints

## Data
For each fluid instance, use only that instance's published labelled dataset (`data/instances/<id>/labels.csv`), the query inputs, and the base-hull library. The labelled dataset is the whole simulation budget. Do not bring in external hydrodynamic labels or physical-test data.

## Evaluator code is not a data source
The development ground truth in `eval/train/` exists to score your work. Do not use it, or its functional form, to generate extra labels, to build a model of the fluid, or to fit the held-out instances. Querying it to design for a development instance is direct optimisation of the scorer. Brute-forcing it does not transfer to the held-out instances and is out of bounds. Do not modify anything under `eval/`.

## Evaluation
Report development scores with `scripts/evaluate_train.sh` (or `scripts/evaluate.sh`). Artifacts go to `outputs/<method>/optimization_results.json` in the format of `briefing/evaluation.md`. The hidden test scores the same artifact on the held-out instances.

## Design Domain
Designs are convex weights over the base-hull library, and the pool angle of attack lies in [-30, 30] degrees. Submissions outside the domain fail.

## Resource Scaling
Any amount of computation on the published data is fine. More simulation labels are not.

## Compliance Checklist
- [ ] Each instance's designs and predictions come only from that instance's published data
- [ ] No use of `eval/` code or ground truth as a model, label source or optimisation target
- [ ] Artifacts in the documented format under `outputs/<method>/`
- [ ] Designs inside the convex hull, angles inside the actuator range
