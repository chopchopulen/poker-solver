"""Vanilla CFR on Kuhn: log exploitability at log-spaced iterations to analysis/kuhn_convergence.csv."""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from eval.exploitability import exploitability


def main(iters=100_000, npoints=40, out="analysis/kuhn_convergence.csv"):
    g = KuhnPoker()
    c = CFR(g)
    checkpoints = sorted(set(np.unique(np.logspace(0, np.log10(iters), npoints).astype(int)).tolist()))
    rows, done, train_time = [], 0, 0.0
    for t in checkpoints:
        t0 = time.perf_counter()
        c.train(t - done)
        train_time += time.perf_counter() - t0  # exclude exploitability eval time
        done = t
        rows.append(("cfr", t, round(train_time, 4), exploitability(g, [c.average_strategy()] * 2)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["solver", "iter", "seconds", "exploitability"])
        w.writerows(rows)
    print(f"kuhn_convergence: {len(rows)} pts, expl iter {rows[0][1]}={rows[0][3]:.4g} -> iter {rows[-1][1]}={rows[-1][3]:.4g}, {train_time:.1f}s -> {out}")


if __name__ == "__main__":
    main()
