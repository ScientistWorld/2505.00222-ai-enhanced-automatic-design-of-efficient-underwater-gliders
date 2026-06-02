from __future__ import annotations

import torch
from torch import nn


class FluidSurrogate(nn.Module):
    """4-layer MLP with batch normalization and tanh nonlinearity."""

    def __init__(self, input_dim: int = 9, hidden_dim: int = 96):
        super().__init__()
        layers = []
        dim = input_dim
        for _ in range(4):
            layers.append(nn.Linear(dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.Tanh())
            dim = hidden_dim
        layers.append(nn.Linear(hidden_dim, 2))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
