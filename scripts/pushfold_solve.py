"""Solve push/fold for stacks 1..20 BB -> analysis/pushfold_ranges.csv, pushfold_summary.csv, plots.
Usage: python scripts/pushfold_solve.py [--iters 2000]  (iters doubles until expl < 1e-3 BB, cap 16000)"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from games.holdem_classes import class_grid_position
from solvers.pushfold import exploitability, solve

ap = argparse.ArgumentParser()
ap.add_argument("--iters", type=int, default=2000)
args = ap.parse_args()

d = np.load("analysis/pushfold_equity.npz")
eq, w = d["eq"], d["w"]
labels = [str(x) for x in d["labels"]]
wsb, wbb = w.sum(axis=1) / w.sum(), w.sum(axis=0) / w.sum()
CHARTS = {2, 5, 10, 15, 20}
rng_rows, summ, res = [], [], {}
for S in range(1, 21):
    it = args.iters
    while True:
        s, c, _ = solve(eq, w, S, iters=it)
        ex = exploitability(eq, w, S, s, c)
        if ex < 1e-3 or it >= 16000:
            break
        it *= 2
    res[S] = (s, c)
    for i, h in enumerate(labels):
        rng_rows.append((S, h, f"{s[i]:.6f}", f"{c[i]:.6f}"))
    summ.append((S, f"{100 * (wsb @ s):.3f}", f"{100 * (wbb @ c):.3f}", f"{ex:.3e}", it))
    print(f"S={S} shove={summ[-1][1]}% call={summ[-1][2]}% expl={ex:.2e} iters={it}", file=sys.stderr)

with open("analysis/pushfold_ranges.csv", "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["stack", "hand", "shove", "call"])
    wr.writerows(rng_rows)
with open("analysis/pushfold_summary.csv", "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["stack", "shove_pct", "call_pct", "exploitability_bb", "iters"])
    wr.writerows(summ)

st = [r[0] for r in summ]
plt.figure(figsize=(6, 4))
plt.plot(st, [float(r[1]) for r in summ], "o-", label="SB shove %")
plt.plot(st, [float(r[2]) for r in summ], "s-", label="BB call %")
plt.xlabel("effective stack (BB)")
plt.ylabel("% of combos")
plt.legend()
plt.grid(alpha=.3)
plt.tight_layout()
plt.savefig("analysis/pushfold_shove_call.png", dpi=120)
plt.close()

pos = [class_grid_position(h) for h in labels]
rk = "AKQJT98765432"
for S in CHARTS:
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, v, name in zip(axs, res[S], ("SB shove", "BB call")):
        g = np.zeros((13, 13))
        for (r, k), p in zip(pos, v):
            g[r, k] = p
        im = ax.imshow(g, vmin=0, vmax=1, cmap="viridis")
        ax.set_xticks(range(13))
        ax.set_yticks(range(13))
        ax.set_xticklabels(rk)
        ax.set_yticklabels(rk)
        ax.set_title(f"{name} prob, stack {S} BB")
    fig.colorbar(im, ax=axs, shrink=.8)
    fig.savefig(f"analysis/pushfold_chart_{S}.png", dpi=110)
    plt.close(fig)
print(f"S=1 shove {summ[0][1]}%, S=20 shove {summ[-1][1]}%, max expl {max(float(r[3]) for r in summ):.2e}")
