# Scoring audit runs

Run `bash redteam/run_bundle.sh` in the gym's existing compute container, or
`bash redteam/<case>/run.sh` for one case. Do not run training on the login node.
Each case produces `status.json`, `scores_train.json`, `scores_test.json` when
accepted, and the exact submitted JSON artifacts. Expected invalid cases retain
an error status instead of claiming a score. Logs and trained checkpoints stay
local and are ignored by git.

`harness.py` saves/restores pre-audit files in ignored `_state/`. It never edits
`eval/`, the hidden test shell script, the Python environment, or evaluator
processes. The hidden test is always `bash scripts/evaluate_test.sh` without
arguments, after the submission process has exited. Every evaluator uses a new
process; no background process exists. Cases are sequential for file isolation.

`payloads.py` uses only scientist-visible data and interfaces. Controlled
mutations of trained outputs reuse the reference artifact, as authorized in the
audit request; enumeration and degenerate submissions generate their own
artifacts without accessing reference or hidden answers. The audit controller,
not a submitted method, reads hidden scores for comparison.

`summarize.py` reads raw scores and the original metric definitions, uses declared
directions and absolute coefficient magnitudes, and divides by per-metric
population standard deviations of two explicitly listed audit cohorts. Since
the later ranked cohort is unknown these are audit rank deltas, not predictions
of an unavailable external leaderboard. It records both a literal weighted sum
over result keys and an alternative averaging within experiments. Raw scores
and Pareto comparisons accompany them.

The stronger computational variant retains the original architecture and
surrogate/CMA-ES procedure, increases interpolation from 3 to the paper's 10
morphs per pair, trains 600 epochs at learning rate .003, and searches 200
generations. Three reference retrainings retain all original default settings,
varying both training and optimization seeds. The one-epoch ablation changes
only training duration; mean-shape and torpedo controls remove design search.
