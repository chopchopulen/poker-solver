"""Solve the market-making game with CFR+; log exploitability by iteration and save the average strategy.
Usage: python scripts/mm_solve.py [--deck 10] [--taker-sees 1] [--noise 0.25] [--iters 2000]"""
import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from eval.exploitability import exploitability
from games.market_making import MMConfig, MarketMakingGame
from solvers.cfr_plus import CFRPlus


def solve(cfg, iters, npoints=12, conv_out=None, strat_out=None):
    g = MarketMakingGame(cfg)
    c = CFRPlus(g)
    cps = sorted(set(np.unique(np.logspace(0, np.log10(iters), npoints).astype(int)).tolist()) | {iters})
    rows, done, secs = [], 0, 0.0
    for t in cps:
        t0 = time.perf_counter()
        c.train(t - done)
        secs += time.perf_counter() - t0
        done = t
        rows.append((t, round(secs, 3), exploitability(g, [c.average_strategy()] * 2)))
    avg = c.average_strategy()
    if conv_out:
        os.makedirs(os.path.dirname(conv_out), exist_ok=True)
        with open(conv_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["iter", "seconds", "exploitability"])
            w.writerows(rows)
    if strat_out:
        with open(strat_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["infoset", "action", "prob"])
            for k in sorted(avg):
                for a, p in avg[k].items():
                    w.writerow([k, a, f"{p:.6f}"])
    return g, avg, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", type=int, default=10)
    ap.add_argument("--taker-sees", type=int, default=1)
    ap.add_argument("--noise", type=float, default=0.25)
    ap.add_argument("--iters", type=int, default=2000)
    a = ap.parse_args()
    cfg = MMConfig(deck_size=a.deck, taker_sees=a.taker_sees, noise_prob=a.noise)
    _, avg, rows = solve(cfg, a.iters, conv_out="analysis/mm_game_convergence.csv",
                         strat_out="analysis/mm_game_strategy.csv")
    print(f"mm_solve: deck={a.deck} sees={a.taker_sees} noise={a.noise} iters={rows[-1][0]} "
          f"expl={rows[-1][2]:.3g} {rows[-1][1]:.1f}s infosets={len(avg)} -> analysis/mm_game_*.csv")
