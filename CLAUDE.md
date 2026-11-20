# Poker Solver — project rules and plan

## Rules (always follow)
- You write all the code for this project. I review and edit.
- Work through the phases in order. A phase is DONE only when its "done when" check passes and tests pass. If the previous phase isn't marked DONE in PROGRESS.md, finish it first.
- Verify every result against known values (Kuhn game value = -1/18). Never fake, guess, or hand-type a result. Every number in analysis/results.md must include the exact command that reproduces it.
- Run `pytest -q` before every commit. Commit after each working step with a clear message.
- If stuck on the same bug for 3 attempts, log it in PROGRESS.md under "Open bugs" with what you tried, and move on to what you can do next.
- After each phase: append a plain-English explanation to LEARNING.md (what it does, the key math in LaTeX, 3 review questions with answers).
- At the end of every run: update PROGRESS.md (done / next / open bugs / numbers so far).
- Keep README.md current: what the project is, how to run it, results table, charts.

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

## Token rules (always follow)
- Be terse. No long explanations in replies; put explanations in LEARNING.md only at the end of a phase.
- Never print or cat large files or logs. Use `head -20` / `tail -20`, or grep for what you need.
- Tests must run in under ~10 seconds: use small iteration counts in tests. Long runs (e.g. 100k CFR iterations) go to a script that writes results to analysis/*.csv; read only the summary line.
- Use `pytest -q` and keep program output to one summary line per run.
- Don't re-read files you already read this session unless they changed.
- Don't refactor or polish working code. Finish the phase, commit, stop.
