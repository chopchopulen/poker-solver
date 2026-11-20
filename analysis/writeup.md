# Poker Solver Writeup

## Method
- **Games:** Kuhn poker (3 cards) and Leduc poker (6 cards, 2 rounds), implemented from scratch in `games/`; a zero-sum market-making card game (MM quotes bid/ask, informed or noise taker); heads-up no-limit push/fold over 169 preflop hand classes.
- **Solvers:** vanilla CFR, CFR+, and external-sampling MCCFR (`solvers/`). Output is always the *average* strategy.
- **Evaluation:** exact best response and exploitability (`eval/`); head-to-head matches use mirrored hands (same cards, seats swapped) and 95% CIs over pair means.
- **Agents:** equilibrium agent, 4 fixed bots (always-call, always-raise, tight, random), exact-BR exploiter, and an adaptive agent (Dirichlet opponent model, blended toward best response, with a safety cap).

## Results
Every row is generated from `analysis/*.csv` by `scripts/make_results_table.py`; the command to reproduce each row is in the last column.

<!-- RESULTS_TABLE_START -->
| Metric | Value | Command |
|--------|-------|---------|
| Kuhn game value (vanilla CFR, 100k iters) | -0.055555 (target -1/18 = -0.055556) | `python scripts/run_kuhn_cfr.py` |
| Kuhn exploitability after 100000 iters (vanilla CFR) | 6.76e-04 (log-log slope -0.544, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr && python analysis/plot_convergence.py` |
| Kuhn exploitability after 100000 iters (CFR+) | 2.14e-06 (log-log slope -0.849, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr_plus && python analysis/plot_convergence.py` |
| CFR+ speedup vs vanilla (iters to expl < 0.001) | 331x (43080 vs 130 iters) | `python scripts/kuhn_convergence.py --solver cfr && python scripts/kuhn_convergence.py --solver cfr_plus` |
| Leduc exploitability (mbb/hand), last checkpoint within 140 s: CFR / CFR+ / MCCFR | 12.26 / 0.0254 / 12.61 | `python scripts/leduc_benchmark.py && python analysis/plot_leduc.py` |
| Exploiter (exact BR) vs bots, mbb/hand ±95% CI, 300k hands each | call +1470±7, raise +2377±14, tight +697±11, random +2367±18 (equilibrium: +636±7, +327±19, +61±11, +716±13) | `python scripts/bot_matches.py --pairs 150000 --seed 0` |
| Adaptive agent vs bots, mbb/hand ±95% CI, 40k hands each (cap 1.0 / cap 0.2) | call +1315±19 / +810±20, raise +2194±40 / +632±51, tight +638±36 / +152±32, random +1715±40 / +881±36; vs equilibrium -1±27 / +7±24 | `python scripts/adaptive_matches.py --pairs 20000 --seed 0` |
| Market-making game: CFR+ exploitability after 2000 iters (deck 10, noise 0.25) | 3.85e-05 | `python scripts/mm_solve.py --iters 2000` |
| Market-making: MM EV vs informed taker, taker_sees 0/1/2 (vs noise flow) | -0.000 / -0.466 / -1.211 (+1.333) | `python scripts/mm_info.py --iters 1000` |
| Market-making: max abs(avg mid - E[V given MM card]) | 3.22 (card 2); spread at grid max 4 | `python scripts/mm_quotes.py` |
| Push/fold (HU NL, stacks 1-20 BB): max exploitability | 9.71e-07 BB/hand (S=15) | `python scripts/pushfold_solve.py` |
| Push/fold shove% / call% (combo-weighted), S=1 / 10 / 20 | 100.0 / 58.1 / 40.3 ; 100.0 / 37.4 / 21.7 | `python scripts/pushfold_solve.py` |
| Push/fold equity table: max Monte Carlo std err | 0.0016 | `python scripts/pushfold_equity.py --boards 120000 --validate` |
<!-- RESULTS_TABLE_END -->

Charts: `analysis/kuhn_convergence.png`, `analysis/leduc_benchmark.png`, `analysis/mm_game_quotes.png`, `analysis/mm_game_info.png`, `analysis/pushfold_shove_call.png`, `analysis/pushfold_chart_{2,5,10,15,20}.png`.

Observations:
- Vanilla CFR reproduces the Kuhn value -1/18; CFR+ needs far fewer iterations (331x fewer to reach exploitability < 0.001).
- On Leduc at equal wall-clock (140 s), CFR+ reaches much lower exploitability than vanilla CFR and MCCFR in this implementation.
- The adaptive agent with cap 0.2 beats every bot and is statistically indistinguishable from break-even against equilibrium (+7±24 mbb/hand); cap 1.0 wins more against bots.
- Market-making (noise_prob 0.25): the MM quotes the widest spread on the grid (4) for every card and every taker information level, so spread did not widen with taker information on this grid. Adverse selection shows up in EV instead: MM EV vs informed flow falls from -0.000 to -0.466 to -1.211 as the taker sees 0/1/2 cards, while noise flow pays +1.333.
- Push/fold: exploitability below 1e-6 BB/hand at every stack 1-20 BB; combo-weighted shove range shrinks from 100% (1 BB) to 40.3% (20 BB). These are equilibria of the modeled game with Monte Carlo equities; comparison with a published chart is pending.

## Limits
- Only Kuhn and Leduc, tiny games; results do not transfer directly to full-scale poker. This does not solve poker.
- Bots are simple fixed strategies; adaptive win rates against stronger or adversarial opponents are untested.
- Leduc exploitability is compared at one wall-clock budget; timings reflect this pure-Python implementation, not an optimized one.
- The adaptive safety cap is a heuristic, not a proven bound on exploitability.
- Match CIs assume iid pair means; they cover sampling noise only.
- The market-making game uses a coarse mid/spread grid; mids only weakly track E[V | MM card] (max deviation 3.22) and the spread result is a grid-ceiling effect.
- Push/fold is a restricted game (no limping, no postflop play) and equities carry Monte Carlo error (max std err 0.0016); its equilibrium is not a full no-limit strategy.
