"""Log-log plot of exploitability vs iterations for every solver in analysis/kuhn_convergence.csv -> analysis/kuhn_convergence.png."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LABELS = {"cfr": "vanilla CFR (average strategy)", "cfr_plus": "CFR+ (linear average)"}


def main(csv_path="analysis/kuhn_convergence.csv", out="analysis/kuhn_convergence.png"):
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    by_solver = {}
    for r in rows:
        by_solver.setdefault(r["solver"], []).append(r)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    slopes = {}
    ref_anchor = None
    for solver, srows in by_solver.items():
        it = np.array([float(r["iter"]) for r in srows])
        ex = np.array([float(r["exploitability"]) for r in srows])
        ax.loglog(it, ex, "o-", ms=3, label=LABELS.get(solver, solver))
        if solver == "cfr" or ref_anchor is None:
            ref_anchor = (it, ex)
        # log-log slope over the last decade of the run (where the trend is clean)
        mask = it >= it[-1] / 10
        slopes[solver] = np.polyfit(np.log(it[mask]), np.log(ex[mask]), 1)[0]

    # O(1/sqrt(T)) reference line anchored at the last point of the vanilla CFR run
    it, ex = ref_anchor
    ref = ex[-1] * np.sqrt(it[-1] / it)
    ax.loglog(it, ref, "k--", lw=1, label=r"$\propto T^{-1/2}$ reference")
    ax.set_xlabel("iterations T")
    ax.set_ylabel("exploitability (game value units)")
    ax.set_title("Kuhn poker: exploitability vs iterations")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)

    slope_txt = ", ".join(f"{s} slope={v:.3f}" for s, v in slopes.items())
    print(f"plot_convergence: {len(rows)} pts, {slope_txt}, wrote {out}")


if __name__ == "__main__":
    main()
