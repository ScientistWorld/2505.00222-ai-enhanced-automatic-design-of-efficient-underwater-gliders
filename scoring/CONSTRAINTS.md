# Scientist Constraints

## Data
Use the provided base shape library and deterministic hydrodynamic evaluator in `data/glider_proxy.py`. Do not add external shape datasets, CFD labels, or physical-test data for scored comparisons unless the scoring files are explicitly updated to define a new benchmark.

## Evaluation
Report scores through `scripts/evaluate.sh`. The evaluator must remain independent of `method/` and must read method artifacts from `outputs/`.

## Design Domain
Submitted designs must use the same normalized shape-parameter vector and angle-of-attack format. Designs should remain in the convex hull of the provided base shapes for direct comparability with the paper's constrained search domain.

## Resource Scaling
Do not improve scores merely by replacing the task with a higher-fidelity simulator, larger external data source, or physical measurements. Improvements should come from better use of the same benchmark data and evaluation interface.

## Compliance Checklist
- [ ] Uses only the provided benchmark data/oracle for scored results
- [ ] Writes design artifacts in the expected `outputs/<method>/optimization_results.json` format
- [ ] Evaluates with `scripts/evaluate.sh`
- [ ] Keeps evaluation code independent of `method/`
- [ ] Keeps submitted designs in the shared shape-parameter design domain
