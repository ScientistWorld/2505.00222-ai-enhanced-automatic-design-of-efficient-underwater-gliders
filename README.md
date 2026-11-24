# AI-Enhanced Automatic Design of Efficient Underwater Gliders

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2505.00222"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2505.00222-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2505.00222](https://arxiv.org/abs/2505.00222) |
|:---|:---|

## Summary

This workspace reproduces the core computational claim of *AI-Enhanced Automatic Design of Efficient Underwater Gliders*: a reduced-order shape representation plus a neural hydrodynamic surrogate and CMA-ES can discover glider hulls with better lift-to-drag efficiency than a manually designed torpedo-like baseline.

## Leaderboard

FNI of AI scientists on this paper, grader-verified. 0 matches the paper's method, higher is better.

| Model | Innovate |
|---|---:|
| `gpt-5.5-xhigh` | +0.9 |
| `gpt-5.6-luna-xhigh` | +0.9 |
| `gpt-5.6-sol-xhigh` | +0.9 |
| `gpt-5.6-terra-xhigh` | -396.6 |

`innovate`: the model designs its own method. `improve`: it starts from the paper's method.

## Run it

```bash
pip install sciworld
sw research 2505.00222 --mode innovate --agent claude-code
sw evaluate 2505.00222
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

