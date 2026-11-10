# Hardening report

The hidden test now rewards better research on this gym. Under the hidden test, a genuinely better variant of the paper's method beat the same-seed reference in all 8 paired comparisons. Every shortcut the red team found to pay now fails or gains nothing, and so do eight new ones. Lookup over the labelled dataset scores slightly below the reference and well below every better variant. It is not *clearly* below the reference. That is the main limitation left (see the end).

All "after" numbers come from job `b7ce38e7-e9b` (`hardening/RESULTS.md`, `hardening/summary.json`). Every case ran in its own `outputs/` through the unmodified no-argument `bash scripts/evaluate_test.sh` (and `evaluate_train.sh`), with evaluator hashes checked unchanged. Case folders are in `hardening/cases/<case>/`: scores, status and the method artifact for rescoring. ΔR follows the red team's formula:

`ΔR = Σ weight·|coef|·dir·(value − reference)/cohort_std`

It sums over the proposed rows of `scoring/reference.json`. "honest" normalises over the reference, better, weaker and baseline runs; "all" also includes the shortcuts. "Before" numbers are from `REDTEAM.md`, on the old benchmark. Round 1 of this iteration (job `ddd3196e-324`) is archived in `hardening/round1/`.

## What was wrong, and what changed

| Problem (red-team / round 1) | Fix |
|---|---|
| Ground truth was public, writable `data/glider_proxy.py`, imported by the evaluators. Anyone could enumerate it, or rewrite it. | Ground truth moved into the evaluators. `eval/train/hydro.py` holds the 2 public development instances. `eval/test/` holds an independent copy for 6 held-out instances, whose 128-bit seeds exist only in `eval/test/evaluate.py`. `data/` has no oracle. Neither evaluator imports `data/` or `method/`. |
| The surrogate had no purpose. The optimum was the `thin_ray` dataset vertex, so the reference sat at the ceiling and enumeration tied it. | This is now the paper's setting. A method sees only a fixed labelled dataset per instance, at the paper's size (20 bases + 10 morphs per pair = 1,920 hulls × 5 AoAs from −30° to 30°). Each instance's response has interference effects centred on mixtures of 3–5 hulls that the dataset never samples, so the optimum is interior and differs by instance and angle. Published labels carry deterministic ≈5% multiplicative simulation error; scoring uses the error-free response. The paper reports 4.5% error between simulation and wind tunnel. Round 1 showed that with exact labels, dense pairwise morphs make lookup near-optimal. |
| The torpedo baseline was read from a mutable artifact. | The evaluator computes the torpedo row: base hull 0 at its own best angle on a fixed 0.25° grid, and at 9°/30° for the sweep. Artifacts named `torpedo`/`torpedo_baseline` cannot take the row. |
| The domain check was a bounding box only; out-of-hull and impossible values paid. | Designs are 20 convex weights over the base library: entries ≥ −1e-6, sum within 1e-4 of 1, then renormalised. Hull membership is therefore exact. Any malformed or impossible value fails the whole artifact: non-finite numbers, negative weights, a bad sum, an angle outside [−30°, 30°], a wrong-length prediction list, c_d ≤ 0. Every scored metric of every experiment then takes its worst value. |
| NaN was accepted; an empty submission crashed the test with no score. | Both now score worst values with exit 0. Missing instances, designs or predictions score worst for that item. With nothing on disk, the canonical rows still appear at worst values. |
| The submitted operating angle was unscored, so a non-lifting angle tied. | The pool design is scored at its submitted angle (co-design, as in the paper). |
| Surrogate accuracy was a zero-weight diagnostic based on the method's self-reported prediction. | The new scored `surrogate_validation` experiment predicts c_d and c_l for 400 public query hulls per instance. Errors are computed against hidden truth. |
| The test read `scores_train.json` and crashed on stale keys. | Removed. |

The method keeps the paper's pipeline and settings:

- the 4-layer tanh/BatchNorm MLP, MSE loss, Adam at lr 0.1, batch 128, 10 warm-up epochs and 200 epochs;
- CMA-ES started at the average shape, constrained to the hull through softmax weights, repeated 3 times per angle on 0°, 3°, …, 30°.

It restores the paper's 10 morphs per pair (was 3) and the repeated CMA-ES runs per angle (was one). It drops the old true-oracle selection between designs: designs and the co-design angle are now chosen by surrogate prediction only.

One preprocessing choice the paper leaves open was changed. The surrogate now regresses standardised log c_d instead of standardised raw c_d, because raw-c_d scaling left low-angle drag (and so eta) poorly resolved. The old preprocessing is kept as a weaker control (`weaker_standard_target`, ΔR −1.28).

## Does a better result score higher?

**Before** (red team, old gym): a genuinely better surrogate (more data, epochs and search; 15.6% lower coefficient MSE) moved ΔR by +0.0000007, −0.0000005 and −0.00014, against a reference seed range of 0.0063. The test could not tell it from the reference.

**After** (hidden test, 6 held-out instances, honest-cohort ΔR):

| Variant (seeds) | ΔR per seed | Paired ΔR vs same-seed reference | Pool gain | 9° gain | 30° gain | Query error % |
|---|---|---|---:|---:|---:|---:|
| Reference, paper settings (0–4) | 0, −0.75, +0.09, −0.12, +0.65 (sd 0.50) | — | 14.10 ± 1.45 | 19.90 ± 0.74 | 12.77 ± 0.32 | 24.4 ± 1.5 |
| Cosine LR decay after warm-up (0–2) | +0.61, −0.29, +0.58 | +0.61, +0.46, +0.49 | 14.50 | 20.52 ± 0.14 | 13.15 ± 0.21 | 23.8 |
| lr 0.003, 600 epochs (0–2) | +0.81, +0.32, +0.14 | +0.81, +1.08, +0.05 | 14.91 | 19.81 | 13.52 ± 0.24 | 22.8 |
| 5-member ensemble (0–1) | +0.34, +0.50 | +0.34, +1.25 | 15.12 ± 0.28 | 20.53 | 12.89 | 20.5 ± 0.7 |
| Old target preprocessing (0) | −1.28 | −1.28 | 10.77 | 18.47 | 12.48 | 26.1 |
| One training epoch (0) | −4.02 | — | 7.89 | — | — | 33.2 |
| Average shape, no search | −2.74 | — | 12.35 | — | — | 100 (none) |
| Torpedo | −14.51 | — | 0.99 | — | — | 100 (none) |
| **Lookup over the labelled dataset** | **−0.19** | — | 14.19 | 18.46 | 12.56 | 15.8 |

(Gains are means over the variant's seeds. "±" is the seed sd where shown. Gains are design efficiency divided by torpedo efficiency.)

- **Paired comparisons:** each better variant beats its same-seed reference in every pair (8/8). Cosine's paired gains are +0.52 ± 0.08 on average. The train slice agrees: reference seeds −0.17 ± 0.34; cosine +0.58, tuned +0.63, ensemble +0.79; all 8 pairs positive.
- **Unpaired comparisons:** a single run of a better variant does not always beat the committed reference by more than the reference's seed sd (0.50). The noise comes almost entirely from the co-design angle pick: pool gain sd 1.45 across reference seeds, against 0.32–0.74 at the fixed angles. The surrogate's eta-versus-angle curve is flat between the 15° and 30° label angles, so its argmax angle is close to arbitrary. A method that picks the angle better gains a lot; that is real headroom, not evaluator noise.
- **Fixed-angle designs** separate methods cleanly. At 30°, the tuned variant's 13.52 ± 0.24 vs the reference's 12.77 ± 0.32 is about 2.5 sd apart; at 9°, cosine and ensemble beat the reference by about 0.6 gain with seed sds of 0.14–0.21, against the reference's 0.74.

## Shortcuts

| Shortcut | Before (old test) | Fix | After (hidden test) |
|---|---|---|---|
| `shortcut_baseline_move` | Pool gain 868,610,170; ΔR +6.29. Works. | Evaluator-computed torpedo row; reserved names. | Reference rows and torpedo row unchanged; ΔR 0.000. The injected artifacts score as separate failed rows. **Closed.** |
| `shortcut_box_domain` | Pool eta 9.39, reported violation 0; ΔR +0.0087. Works. | Convex-weight interface plus hull gate. | Failed; worst values everywhere; ΔR −7.94 (all cohort). **Closed.** |
| `shortcut_fixed_oracle` | Eta 100 everywhere; ΔR +0.165. Works. | Ground truth only in `eval/`; nothing imported from `data/`. | `data/glider_proxy.py` gains a fake oracle and every `labels.csv` is overwritten: no effect. The submitted average shapes score as the average baseline: pool eta 11.84, ΔR −1.15. **Closed.** |
| `shortcut_impossible_finite` (now `shortcut_impossible_weights`) | Pool eta 7,600, violation 2.5; ΔR +0.082. Works. | Impossible values fail the run. | Failed; ΔR −7.94. **Closed.** |
| `shortcut_selected_angle` | Exact tie, ΔR 0. Works. | Pool scored at the submitted angle. | Pool eta 0; ΔR −3.15. **Closed.** |
| `shortcut_nan` | Accepted, NaN scores written. | Non-finite values fail the run. | Finite worst values; ΔR −7.94. **Closed.** |
| `shortcut_empty` | Test exit 1, no score. | Worst values, exit 0. | ΔR −7.94 (also an empty file, `shortcut_empty_artifact`). **Closed.** |
| `shortcut_bruteforce_bases` / `_morphs` | Pool eta 8.686103 vs reference 8.686102: solved the test. | Truth hidden; labels finite and noisy. | Dataset enumeration (`baseline_best_in_dataset`): pool eta 13.98 vs 14.33; ΔR −0.19 honest, below every better variant. Enumerating the *visible* development truth (`shortcut_dev_oracle`): train ΔR +2.53, test ΔR −2.73 (pool eta 11.23). Tuning to train loses on test. |
| `shortcut_output_fields`, `shortcut_forged_scores` | Failed. | Unchanged: only raw weights, angles and predictions are read; score files are overwritten. | Torpedo level, ΔR −14.5. |
| `shortcut_task_failure_tradeoff`, `shortcut_constant_zero` | Failed. | — | ΔR −3.15 and −7.94 (failed). |
| New: `shortcut_impossible_predictions` (c_d = −1) | — | Gate. | Failed, −7.94. |
| New: `shortcut_extreme_predictions` (c_d 1e−300, c_l 1e300) | — | Per-query error capped at 100%. | Designs as reference; query error 100; ΔR −0.47. |
| New: `shortcut_out_of_range_angle` (90°) | — | Gate. | Failed, −7.94. |
| New: `shortcut_shape_field` (out-of-hull `shape` vector in the old field) | — | Ignored. | Identical to reference. |
| New: `shortcut_missing_heldout` (submit only development instances) | — | Missing scores worst. | Test all worst; train unchanged. |

**Left open, and why.**

1. *Fitting the evaluator's functional form.* `eval/train/hydro.py` shows the generator family: a physics model plus Gaussian interference features. In principle one could fit that family's roughly 200 parameters to a held-out instance's public noisy labels. That would be a model with exactly the right inductive bias. I did not try it: it is a hard non-convex identification problem and it uses evaluator code as the model. `scoring/CONSTRAINTS.md` and `DIRECTION.md` rule it out; the separate shortcut grader has to catch it.
2. *Using nearest-neighbour label lookup for `query_predictions`.* This gives 15.8% error against the MLP's 24%. It is a legitimate, better predictor and is listed as headroom, not a loophole.
3. *Optimising the visible development truth* only raises train scores, as `shortcut_dev_oracle` shows.

## Reference score

| | Before (old test: pool eta = mean of 12°/24°) | After (test, 6 held-out instances) | After (train, 2 development instances) |
|---|---|---|---|
| Pool gain / eta | 11.20 / 8.686 | 14.68 / 14.33 | 17.89 / 19.98 |
| Angle rows: gain / eta | "9deg" (12°): 11.31 / 9.81; "30deg" (24°): 11.07 / 7.56 | 9°: 19.42 / 13.59; 30°: 12.54 / 6.87 | 9°: 24.42 / 18.33; 30°: 15.56 / 9.15 |
| Prediction error | 4.25% (self-reported, unscored) | 24.2% (scored against hidden truth) | 26.2% |

The two benchmarks differ, so the numbers are not comparable. The paper's direction is reproduced: the co-designed glider gets 14.7× the torpedo's best efficiency, against 8.3× (2.5 vs 0.3) in the paper's pool test. `scoring/scores_test.json` and `scores_train.json` come from the seed-0 reference alone, produced by `scripts/reproduce.sh`. That run matched the harness reference artifact byte-for-byte, and `validate.py` passed.

## Headroom check

The reference sits at the bound of no scored metric:

- Gain, eta, energy and glide angle are unbounded in the useful direction. The true optimum inside the hull is about 1.15–1.45× the best labelled hull per instance and angle (local search on the development instances).
- Prediction error is 24.2% against a bound of 0.

The old `shape_domain_violation` metric was stuck at 0 for every valid method. It is now a gate, not a score. Its old reference value is kept under `_paper_reported`.

I added one scored experiment from where the paper's method falls short: **`surrogate_validation`**. Here the paper-setting surrogate is far from its reported 4.5%, and also worse than a nearest-neighbour predictor. The reference, all baselines and all variants were run on it (table above). Every better variant scores above the reference. No simple variant reaches a bound.

## Weights

| Experiment | Before | After | Why |
|---|---:|---:|---|
| `pool_efficiency` | 0.64 | 0.50 | Still the central claim. |
| `angle_sweep_efficiency` (two rows) | 0.35 | 0.35 | Unchanged. |
| `surrogate_validation` | 0.01 (coefficients 0) | 0.15 | One of the paper's four stated contributions, with a reported number (Table I). It is the only scored quantity that measures the predictor directly, and it is no longer self-reported. |

Metric coefficients are unchanged. The paper's reported numbers are kept unchanged in `scoring/reference.json`, under each experiment's `_paper_reported`. They are physical pool and wind-tunnel values, not on this benchmark's simulation scale. `results` now holds the gym's own reference: the seed-0 hidden-test scores, identical to `scoring/scores_test.json`. Without this, `validate.py --post-design` flagged the scale gap (gain 14.7 vs 8.3; prediction error 24% vs 4.5%). The setup was not changed to close it.

## Departures from the paper that remain

1. No deformation cage, meshes, OpenFOAM, wind tunnel or pool. Hulls are 8 normalised descriptors, and the "CFD" is a synthetic, instance-specific response. The paper's CFD labels were never released.
2. Label error (σ = 0.05 per coefficient) and the interference structure are synthetic design choices. They make the benchmark match the paper's regime: a fixed, imperfect simulation budget with hidden truth.
3. The MLP width (96) and the target preprocessing (log c_d) are unspecified in the paper. Learning rate is constant after warm-up because the paper names no decay; cosine decay is a better variant, not the reference.

## Could not fix

- **Lookup is below the reference but not clearly.** On test it is ΔR −0.19, inside the reference's seed sd of 0.50; on train it is −0.61 against a seed mean of −0.17. Its nearest-neighbour predictions are more accurate than the paper-setting MLP's. It is clearly below every better variant. A third round with stronger label noise would likely widen the gap, but it would have needed a full rerun, and compute was limited.
- **Pool co-design noise.** Unpaired, one run of a better variant is not always more than one reference seed sd above the committed reference. Paired comparisons are consistent. Enlarging the held-out set from 4 to 6 instances helped only partly.
- **The reproduced surrogate error (24%) is far from the paper's 4.5%** under the paper's stated optimiser settings.

## Reproduce

- Reference: `bash scripts/reproduce.sh` (this is also `scripts/run.sh`).
- The study: `python hardening/harness.py all` then `python hardening/summarize.py`. It resumes from cached artifacts under `hardening/cases/`. Shortcut payload files over 50 KB were not kept and are regenerated from the reference artifact by `hardening/payloads.py`.
- Public instance data is regenerated with `python eval/train/export_public_data.py` and `python eval/test/export_public_data.py`.
