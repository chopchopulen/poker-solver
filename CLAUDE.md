# Poker Solver — project rules and plan

## Rules (always follow)
- I HAND-WRITE the core logic: games/kuhn.py, games/leduc.py, solvers/cfr.py, solvers/cfr_plus.py, eval/best_response.py. Never write these files. If I'm stuck: hints, pseudocode, or point at the bug — then I fix it.
- You MAY write: scaffolding, the Game interface skeleton (signatures + docstrings only), tests, plots, CLI, bots, README drafts.
- Before each phase: explain the concepts (math in LaTeX) and quiz me with 2-3 questions.
- Verify everything against known results (Kuhn game value = -1/18). Never accept an unverified result.
- At the END of every session, update PROGRESS.md: what got done, what's next, open bugs.
- I make my own commits for core files.

## Stack
Python 3.11, numpy, pytest, matplotlib. Run tests with `pytest -q`.

## Structure
games/ (base.py, kuhn.py, leduc.py) · solvers/ (cfr.py, cfr_plus.py, mccfr.py) · eval/ (best_response.py, exploitability.py, match.py) · agents/ (equilibrium, bots, exploiter, adaptive) · play/cli.py · analysis/ (plots, results.md) · tests/ · LEARNING.md (my notes) · PROGRESS.md (session log)

## Phases ("done when")
1. Kuhn + vanilla CFR -> converges to -1/18 and the known equilibrium family
2. Best response + exploitability -> log-log convergence plot
3. CFR+ -> faster convergence on the same plot
4. Leduc + Monte Carlo CFR (external sampling) -> exploitability (mbb/hand) vs time, all solvers
5. Bots (always-call, always-raise, tight, random) + best response vs each -> win rates with 95% CIs over many mirrored hands
6. Adaptive agent: models opponent online, safely shifts from equilibrium toward exploitation
7. Terminal play mode vs the bot, showing its strategy
8. README + short writeup with results table

## Pitfalls to watch
Use the AVERAGE strategy, not the current one · info-set keys contain only what the player can see · weight chance nodes by probability · head-to-head results need many hands + CIs · never claim "solved poker"

## Add-ons (after phase 8)
No-limit push/fold solver checked against published charts · CFR on a card-sum market-making game · analysis of my own tournament hand histories · precomputed strategy tables for <1ms decisions (No Limit tournament)

