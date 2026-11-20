"""Log-log plot of exploitability vs iterations from analysis/kuhn_convergence.csv -> analysis/kuhn_convergence.png."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main(csv_path="analysis/kuhn_convergence.csv", out="analysis/kuhn_convergence.png"):
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    it = np.array([float(r["iter"]) for r in rows])
    ex = np.array([float(r["exploitability"]) for r in rows])

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.loglog(it, ex, "o-", ms=3, label="vanilla CFR (average strategy)")
    # O(1/sqrt(T)) reference line anchored at the last point
    ref = ex[-1] * np.sqrt(it[-1] / it)
    ax.loglog(it, ref, "k--", lw=1, label=r"$\propto T^{-1/2}$ reference")
    ax.set_xlabel("iterations T")
    ax.set_ylabel("exploitability (game value units)")
    ax.set_title("Kuhn poker: CFR exploitability vs iterations")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)

    # log-log slope over the second half of the run (where the trend is clean)
    mask = it >= it[-1] / 10
    slope = np.polyfit(np.log(it[mask]), np.log(ex[mask]), 1)[0]
    print(f"plot_convergence: {len(rows)} pts, slope(T>={int(it[-1] / 10)})={slope:.3f}, wrote {out}")


if __name__ == "__main__":
    main()
