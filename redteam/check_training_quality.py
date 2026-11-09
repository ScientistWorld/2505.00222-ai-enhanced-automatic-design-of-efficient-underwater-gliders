"""Common public-oracle validation of existing checkpoints; no hidden inputs.

This diagnostic does not generate a new submission or change scoring. Its only
purpose is to distinguish better fitting from merely larger compute budgets.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from data.glider_proxy import base_shape_library, hydrodynamic_coefficients
from method.model import FluidSurrogate


def main():
    torch.set_num_threads(1)
    rng = np.random.default_rng(20261109)
    bases, _ = base_shape_library()
    weights = rng.dirichlet(np.full(len(bases), .2), size=2048)
    shapes = (weights @ bases).astype(np.float32)
    angles = rng.uniform(-30., 30., len(shapes)).astype(np.float32)
    x = np.column_stack([shapes, angles / 30.]).astype(np.float32)
    cd, cl = hydrodynamic_coefficients(shapes, angles)
    truth = np.column_stack([cd, cl])
    true_eta = cl / cd
    lifting = (angles > 0) & (cl > .05)
    paths = {'saved_reference': Path('checkpoints/fluid_surrogate.pt')}
    for prefix in ['reference_seed', 'better_seed']:
        for seed in range(3):
            name = prefix + str(seed)
            paths[name] = Path('redteam') / name / 'checkpoint.pt'
    results = {}
    for name, path in paths.items():
        checkpoint = torch.load(path, map_location='cpu')
        model = FluidSurrogate(input_dim=9)
        model.load_state_dict(checkpoint['state_dict'])
        model.eval()
        with torch.no_grad():
            pred = model(torch.tensor(x)).numpy()
        pred = pred * np.asarray(checkpoint['target_std']) + np.asarray(checkpoint['target_mean'])
        pred = np.maximum(pred, 1e-6)
        predicted_eta = pred[:, 1] / pred[:, 0]
        results[name] = {
            'common_coefficients_mse': float(np.mean((pred-truth)**2)),
            'cd_rmse': float(np.sqrt(np.mean((pred[:, 0]-cd)**2))),
            'cl_rmse': float(np.sqrt(np.mean((pred[:, 1]-cl)**2))),
            'positive_angle_eta_mape_percent': float(np.mean(np.abs(
                predicted_eta[lifting]-true_eta[lifting])/true_eta[lifting])*100.),
            'best_epoch': checkpoint.get('best_epoch'),
            'training_checkpoint_best_val_mse': checkpoint.get('best_val_mse'),
            'trained_epochs': len(checkpoint.get('history', [])),
        }
    output = {
        'diagnostic_only': True,
        'dataset': '2048 independent Dirichlet(.2) convex combinations and uniform AoAs over [-30,30]; labels computed by the original public oracle',
        'seed': 20261109, 'positive_lifting_samples': int(lifting.sum()),
        'results': results,
    }
    Path('redteam/training_quality.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
