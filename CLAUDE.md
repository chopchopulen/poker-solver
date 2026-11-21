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
Python 3.14 (tested), numpy, pytest, matplotlib, treys. Run tests with `pytest -q`.

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
9. Market-making card game solved with CFR+ -> exploitability ~0, quotes track E[V|card], spread vs taker info, adverse selection (spec below)
10. HU no-limit push/fold solver -> 169x169 equity table, equilibrium per stack 1-20 BB, exploitability ~0, range charts, query tool (spec below)

## Pitfalls to watch
Use the AVERAGE strategy, not the current one · info-set keys contain only what the player can see · weight chance nodes by probability · head-to-head results need many hands + CIs · never claim "solved poker"

## Phase 9 spec — market-making card game
- games/market_making.py implements Game. Cards 1..N (default 10) dealt w/o replacement: MM card, taker card, 1 hidden card. V = sum of 3 cards.
- MM picks (mid, spread) from a small grid -> bid = mid - s/2, ask = mid + s/2. Taker sees quote, picks buy/sell/pass. Taker buy: taker +V-ask, MM -(V-ask); sell: taker +bid-V. Zero-sum, 1 unit.
- Config: deck size, mid grid, spread grid, taker_sees in {0,1,2} (0 = nothing, 1 = own card, 2 = own + hidden), noise_prob (chance: taker is a noise trader who buys/sells/passes uniformly), rounds in {1,2}.
- Why noise: with only an informed zero-sum taker, MM's best quote is the widest spread (no trade). Noise flow pays the spread (Glosten-Milgrom). Report results for noise_prob > 0 and say so.
- Solve with existing CFR+/eval.exploitability. Keep tree small (1-round default ~10^5 nodes); 2-round uses a smaller deck/grid.
- Done when: exploitability ~0; avg mid per MM card near E[V | MM card]; spread vs taker_sees reported (expected to widen); MM loss vs informed vs uninformed taker; analysis/mm_game*.csv + plots; tests; LEARNING.md (Glosten-Milgrom, adverse selection); README section. No overclaims.

## Phase 10 spec — HU no-limit push/fold
- SB shoves or folds; BB calls or folds; blinds 0.5/1; effective stack S in 1..20 BB. Payoffs (SB, in BB): fold -0.5; shove/fold +1; shove/call S*(2*eq-1).
- 169 hand classes (13 pairs x6 combos, 78 suited x4, 78 offsuit x12). Equity table 169x169 combo-weighted with card removal; joint weight w[i][j] = # non-conflicting combo pairs. Evaluator: eval7 (fallback treys). Cache to analysis/pushfold_equity.npz.
- Solve per stack (vectorized CFR+ or fictitious play over classes); exploitability via best response, in BB.
- Outputs: 13x13 range charts, shove%/call% vs stack plot, `python -m play.pushfold --stack 10 --hand AJo`.
- Verify: exploitability ~0; ranges widen as S shrinks; very short stacks shove nearly all. External chart comparison ONLY if a source is actually accessed; else write "external comparison pending". Never invent chart values.

## Token rules (always follow)
- Be terse. No long explanations in replies; put explanations in LEARNING.md only at the end of a phase.
- Never print or cat large files or logs. Use `head -20` / `tail -20`, or grep for what you need.
- Tests must run in under ~10 seconds: use small iteration counts in tests. Long runs (e.g. 100k CFR iterations) go to a script that writes results to analysis/*.csv; read only the summary line.
- Use `pytest -q` and keep program output to one summary line per run.
- Don't re-read files you already read this session unless they changed.
- Don't refactor or polish working code. Finish the phase, commit, stop.
