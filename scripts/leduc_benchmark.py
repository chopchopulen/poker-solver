"""Leduc: CFR, CFR+, MCCFR for a fixed wall-clock budget each -> analysis/leduc_benchmark.csv
(solver, seconds = training time only, iters, exploitability, mbb_per_hand).
Usage: python scripts/leduc_benchmark.py [--budget SECONDS_PER_SOLVER]"""
import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.leduc import LeducPoker
from solvers.cfr import CFR
from solvers.cfr_plus import CFRPlus
from solvers.mccfr import MCCFR
from eval.exploitability import exploitability, to_mbb_per_hand

# (class, initial iterations per chunk); chunk grows 1.3x between evaluations
SOLVERS = {"cfr": (CFR, 5), "cfr_plus": (CFRPlus, 5), "mccfr": (MCCFR, 500)}


def run(name, g, budget):
    """Train in growing chunks; budget bounds wall-clock (train + eval)."""
    cls, chunk = SOLVERS[name]
    s, rows, it, train_t = cls(g), [], 0, 0.0
    start = time.perf_counter()
    while time.perf_counter() - start < budget:
        t0 = time.perf_counter()
        s.train(chunk)
        train_t += time.perf_counter() - t0
        it += chunk
        e = exploitability(g, [s.average_strategy()] * 2)
        rows.append([name, round(train_t, 3), it, e, to_mbb_per_hand(e)])
        chunk = max(chunk + 1, int(chunk * 1.3))
    return rows


def main(budget=140, out="analysis/leduc_benchmark.csv"):
    g = LeducPoker()
    allrows = []
    for n in SOLVERS:
        r = run(n, g, budget)
        allrows += r
        print(f"{n}: iters={r[-1][2]} train_s={r[-1][1]:.1f} expl={r[-1][3]:.4g} mbb/hand={r[-1][4]:.1f}")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["solver", "seconds", "iters", "exploitability", "mbb_per_hand"])
        w.writerows(allrows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=140)
    main(ap.parse_args().budget)
