# Poker Solver

## Overview
Counterfactual Regret Minimization (CFR) solvers for small poker games, built from scratch in Python.
The project computes approximate Nash equilibria for Kuhn and Leduc poker, measures how close they are
to equilibrium (exploitability), and uses them to build bots, an exploiting agent, and an adaptive agent
that shifts from equilibrium play toward exploiting a weak opponent.

All results are verified against known values (e.g. Kuhn poker game value = -1/18 for player 1).

**Status:** Phase 1 (Kuhn + vanilla CFR) not started. See [PROGRESS.md](PROGRESS.md).

## Quickstart
Requires Python 3.11.

```bash
pip install numpy pytest matplotlib
pytest -q
```

Solver, evaluation, and play commands will be added here as each phase lands.

## Games
| Game  | Deck | Rounds | Notes |
|-------|------|--------|-------|
| Kuhn  | 3 cards (J, Q, K) | 1 | Known closed-form equilibrium family; game value -1/18 |
| Leduc | 6 cards (2 suits × J, Q, K) | 2 (one private card, one public card) | Standard CFR benchmark |

## Solvers
| Solver | Description |
|--------|-------------|
| Vanilla CFR | Full-tree traversal; regret matching; average strategy converges to Nash at $O(1/\sqrt{T})$ |
| CFR+ | Regrets floored at zero, linearly weighted averaging; typically much faster in practice |
| MCCFR (external sampling) | Samples chance and opponent actions; cheaper iterations for larger games |

Evaluation: exact best response and exploitability (reported in mbb/hand for Leduc).

## Results
Every number below will link to the exact command that reproduces it (see `analysis/results.md`).

| Metric | Value | Command |
|--------|-------|---------|
| Kuhn game value (vanilla CFR) | TBD | TBD |
| Kuhn exploitability after N iters (vanilla CFR) | TBD | TBD |
| Kuhn exploitability after N iters (CFR+) | TBD | TBD |
| CFR+ speedup vs vanilla (iters to target exploitability) | TBD | TBD |
| Leduc exploitability (mbb/hand), all solvers | TBD | TBD |
| Best response win rate vs bots (95% CI) | TBD | TBD |
| Adaptive agent win rate vs bots (95% CI) | TBD | TBD |

## Charts
_None yet._ Planned:
- Kuhn exploitability vs iterations (log-log), vanilla CFR vs CFR+
- Leduc exploitability (mbb/hand) vs wall-clock time, all solvers

## What I learned
Detailed notes per phase in [LEARNING.md](LEARNING.md). Summary will be filled in as phases complete.
