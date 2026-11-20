# Poker Solver Writeup

## Method
- **Games:** Kuhn poker (3 cards) and Leduc poker (6 cards, 2 rounds), implemented from scratch in `games/`.
- **Solvers:** vanilla CFR, CFR+, and external-sampling MCCFR (`solvers/`). Output is always the *average* strategy.
- **Evaluation:** exact best response and exploitability (`eval/`); head-to-head matches use mirrored hands (same cards, seats swapped) and 95% CIs over pair means.
- **Agents:** equilibrium agent, 4 fixed bots (always-call, always-raise, tight, random), exact-BR exploiter, and an adaptive agent (Dirichlet opponent model, blended toward best response, with a safety cap).

## Results
Every row is generated from `analysis/*.csv` by `scripts/make_results_table.py`; the command to reproduce each row is in the last column.

| Metric | Value | Command |
|--------|-------|---------|
| Kuhn game value (vanilla CFR, 100k iters) | -0.055555 (target -1/18 = -0.055556) | `python scripts/run_kuhn_cfr.py` |
| Kuhn exploitability after 100000 iters (vanilla CFR) | 6.76e-04 (log-log slope -0.544, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr && python analysis/plot_convergence.py` |
| Kuhn exploitability after 100000 iters (CFR+) | 2.14e-06 (log-log slope -0.849, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr_plus && python analysis/plot_convergence.py` |
| CFR+ speedup vs vanilla (iters to expl < 0.001) | 331x (43080 vs 130 iters) | `python scripts/kuhn_convergence.py --solver cfr && python scripts/kuhn_convergence.py --solver cfr_plus` |
| Leduc exploitability (mbb/hand), last checkpoint within 140 s: CFR / CFR+ / MCCFR | 12.26 / 0.0254 / 12.61 | `python scripts/leduc_benchmark.py && python analysis/plot_leduc.py` |
| Exploiter (exact BR) vs bots, mbb/hand ±95% CI, 300k hands each | call +1470±7, raise +2377±14, tight +697±11, random +2367±18 | `python scripts/bot_matches.py --pairs 150000 --seed 0` |
| Adaptive agent vs bots (cap 1.0 / cap 0.2), 40k hands each | call +1315±19 / +810±20, raise +2194±40 / +632±51, tight +638±36 / +152±32, random +1715±40 / +881±36; vs equilibrium -1±27 / +7±24 | `python scripts/adaptive_matches.py --pairs 20000 --seed 0` |

Charts: `analysis/kuhn_convergence.png`, `analysis/leduc_benchmark.png`.

Observations:
- Vanilla CFR reproduces the Kuhn value -1/18; CFR+ needs far fewer iterations (331x fewer to reach exploitability < 0.001).
- On Leduc at equal wall-clock (140 s), CFR+ reaches much lower exploitability than vanilla CFR and MCCFR in this implementation.
- The adaptive agent with cap 0.2 beats every bot and is statistically indistinguishable from break-even against equilibrium (+7±24 mbb/hand); cap 1.0 wins more against bots.

## Limits
- Only Kuhn and Leduc, tiny games; results do not transfer directly to full-scale poker. This does not solve poker.
- Bots are simple fixed strategies; adaptive win rates against stronger or adversarial opponents are untested.
- Leduc exploitability is compared at one wall-clock budget; timings reflect this pure-Python implementation, not an optimized one.
- The adaptive safety cap is a heuristic, not a proven bound on exploitability.
- Match CIs assume iid pair means; they cover sampling noise only.
