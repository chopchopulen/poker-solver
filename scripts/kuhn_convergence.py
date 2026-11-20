"""CFR / CFR+ on Kuhn: exploitability at log-spaced iterations -> analysis/kuhn_convergence.csv (rows per solver replaced);
when both solvers present, also iters-to-1e-3 speedup -> analysis/kuhn_speedup.csv.
Usage: python scripts/kuhn_convergence.py [--solver cfr|cfr_plus]"""
import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from solvers.cfr_plus import CFRPlus
from eval.exploitability import exploitability


SOLVERS = {"cfr": CFR, "cfr_plus": CFRPlus}
TARGET = 1e-3


def iters_to_target(name, g, target=TARGET, step=10, cap=500_000):
    """First multiple of `step` iterations whose average strategy has exploitability < target."""
    c, t = SOLVERS[name](g), 0
    while t < cap:
        c.train(step)
        t += step
        if exploitability(g, [c.average_strategy()] * 2) < target:
            return t
    raise RuntimeError(f"{name} did not reach {target} in {cap} iters")


def write_speedup(out="analysis/kuhn_speedup.csv"):
    g = KuhnPoker()
    it = {n: iters_to_target(n, g) for n in SOLVERS}
    sp = it["cfr"] / it["cfr_plus"]
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target_exploitability", "cfr_iters", "cfr_plus_iters", "speedup"])
        w.writerow([TARGET, it["cfr"], it["cfr_plus"], round(sp, 2)])
    print(f"kuhn_speedup: iters to expl<{TARGET:g}: cfr={it['cfr']} cfr_plus={it['cfr_plus']} speedup={sp:.1f}x -> {out}")


def main(solver="cfr", iters=100_000, npoints=40, out="analysis/kuhn_convergence.csv"):
    g = KuhnPoker()
    c = SOLVERS[solver](g)
    checkpoints = sorted(set(np.unique(np.logspace(0, np.log10(iters), npoints).astype(int)).tolist()))
    rows, done, train_time = [], 0, 0.0
    for t in checkpoints:
        t0 = time.perf_counter()
        c.train(t - done)
        train_time += time.perf_counter() - t0  # exclude exploitability eval time
        done = t
        rows.append((solver, t, round(train_time, 4), exploitability(g, [c.average_strategy()] * 2)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    old = []
    if os.path.exists(out):
        with open(out, newline="") as f:
            old = [r for r in list(csv.reader(f))[1:] if r[0] != solver]  # keep other solvers' rows
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["solver", "iter", "seconds", "exploitability"])
        w.writerows(old)
        w.writerows(rows)
    print(f"kuhn_convergence: {len(rows)} pts, expl iter {rows[0][1]}={rows[0][3]:.4g} -> iter {rows[-1][1]}={rows[-1][3]:.4g}, {train_time:.1f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", choices=list(SOLVERS), default="cfr")
    a = ap.parse_args()
    main(a.solver)
    with open("analysis/kuhn_convergence.csv", newline="") as f:
        have = {r[0] for r in list(csv.reader(f))[1:]}
    if have >= set(SOLVERS):
        write_speedup()
