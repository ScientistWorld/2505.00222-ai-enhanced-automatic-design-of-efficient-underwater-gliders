"""Archive explicit, cohort-normalized rank deltas without editing gym scoring."""
from __future__ import annotations

import json
from pathlib import Path
import math
import statistics

ROOT = Path('/home/user')
AUDIT = ROOT / 'redteam'
KEYS = {'pool_efficiency': ['ai_enhanced_glider'],
        'angle_sweep_efficiency': ['ai_enhanced_9deg', 'ai_enhanced_30deg']}


def main():
    definitions = json.loads((ROOT / 'scoring/reference.json').read_text())['experiments']
    columns, weights = [], []
    for experiment, keys in KEYS.items():
        definition = definitions[experiment]
        for key in keys:
            for metric, spec in definition['metrics'].items():
                if abs(spec['coefficient']) == 0:
                    continue
                columns.append((experiment, key, metric, spec['higher_is_better']))
                weights.append(definition['weight'] * abs(spec['coefficient']))
    scores, rows, statuses = {}, {}, {}
    for folder in sorted(AUDIT.iterdir()):
        if not folder.is_dir() or not (folder / 'status.json').exists():
            continue
        statuses[folder.name] = json.loads((folder / 'status.json').read_text())
        scorefile = folder / 'scores_test.json'
        if not scorefile.exists():
            continue
        obj = json.loads(scorefile.read_text())
        scores[folder.name] = obj
        try:
            values = [float(obj['experiments'][exp]['results'][key][metric])
                      for exp, key, metric, _ in columns]
        except (KeyError, TypeError, ValueError):
            continue
        if all(math.isfinite(v) for v in values):
            rows[folder.name] = values
    reference = rows['reference']
    honest = [n for n in rows if n == 'reference' or n.startswith(('reference_seed', 'better_', 'weaker_'))]
    cohorts = {'honest': honest, 'all_finite_audit': list(rows)}
    rank_tables, std_tables = {}, {}
    for cohort, names in cohorts.items():
        deviations = [statistics.pstdev([rows[n][i] for n in names]) for i in range(len(columns))]
        std_tables[cohort] = deviations
        table = {}
        for name, row in rows.items():
            terms = [weights[i] * (1 if columns[i][3] else -1) * (v-reference[i]) / std
                     if std > 1e-12 else 0. for i, (v, std) in enumerate(zip(row, deviations))]
            table[name] = {'rank_delta': sum(terms),
                           'rank_delta_experiment_mean': sum(
                               term / len(KEYS[columns[i][0]]) for i, term in enumerate(terms)),
                           'terms': terms}
        rank_tables[cohort] = table
    seed_names = ['reference_seed0', 'reference_seed1', 'reference_seed2']
    seed_spread = {}
    for cohort in cohorts:
        vals = [rank_tables[cohort][n]['rank_delta'] for n in seed_names if n in rows]
        seed_spread[cohort] = {'seeds': vals, 'min': min(vals), 'max': max(vals),
                               'range': max(vals)-min(vals)} if vals else {}
    raw_spread = []
    for i, column in enumerate(columns):
        vals = [rows[n][i] for n in seed_names if n in rows]
        raw_spread.append({'column': column, 'values': vals,
                           'range': max(vals)-min(vals)} if vals else {})
    out = {'normalization_note': 'External future cohort is unknown. Reported ranks use explicit audit cohorts, population std, abs coefficients, declared directions, sum over proposed result keys, and runtime reference scores, not paper physical values. Baseline rows are controls, not submissions. Constant columns contribute zero. Raw metrics are authoritative; Pareto comparisons are cohort independent.',
           'columns': columns, 'weights': weights, 'cohorts': cohorts,
           'cohort_std': std_tables, 'rank_tables': rank_tables,
           'seed_rank_spread': seed_spread, 'seed_raw_spread': raw_spread,
           'statuses': statuses}
    (AUDIT / 'summary.json').write_text(json.dumps(out, indent=2) + '\n')
    lines = ['| Run | Pool eta | 12° eta | 24° eta | Pool gain | Domain | Rank Δ (honest σ) | Rank Δ (all σ) |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name, status in statuses.items():
        if name not in rows:
            outcome = (f"rejected (exit {status.get('test_exit', 'unknown')})"
                       if status.get('test_exit') != 0 else 'accepted; nonfinite scores')
            lines.append(f'| {name} | {outcome} | | | | | | |')
            continue
        exps = scores[name]['experiments']
        pool = exps['pool_efficiency']['results']['ai_enhanced_glider']
        angle = exps['angle_sweep_efficiency']['results']
        lines.append(f"| {name} | {pool['lift_to_drag']:.9g} | {angle['ai_enhanced_9deg']['lift_to_drag']:.9g} | {angle['ai_enhanced_30deg']['lift_to_drag']:.9g} | {pool['efficiency_gain_over_torpedo']:.9g} | {pool['shape_domain_violation']:.9g} | {rank_tables['honest'][name]['rank_delta']:.7g} | {rank_tables['all_finite_audit'][name]['rank_delta']:.7g} |")
        directional = [(1 if columns[i][3] else -1) * (v-reference[i]) for i, v in enumerate(rows[name])]
        comparison = {'honest_normalized_delta': rank_tables['honest'][name],
                      'all_audit_normalized_delta': rank_tables['all_finite_audit'][name],
                      'directional_deltas': directional,
                      'pareto_no_worse': all(v >= -1e-7 for v in directional),
                      'pareto_no_better': all(v <= 1e-7 for v in directional)}
        (AUDIT / name / 'comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
    (AUDIT / 'RESULTS.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print('Seed rank spread:', seed_spread)


if __name__ == '__main__':
    main()
