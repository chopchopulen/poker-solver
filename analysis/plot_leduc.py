"""Log-scale plot of exploitability (mbb/hand) vs training seconds for every solver in analysis/leduc_benchmark.csv -> analysis/leduc_benchmark.png."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LABELS = {
    "cfr": "vanilla CFR",
    "cfr_plus": "CFR+",
    "mccfr": "MCCFR (external sampling)",
}


def main(csv_path="analysis/leduc_benchmark.csv", out="analysis/leduc_benchmark.png"):
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    by_solver = {}
    for r in rows:
        by_solver.setdefault(r["solver"], []).append(r)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for solver, srows in by_solver.items():
        sec = np.array([float(r["seconds"]) for r in srows])
        mbb = np.array([float(r["mbb_per_hand"]) for r in srows])
        ax.semilogy(sec, mbb, "o-", ms=3, label=LABELS.get(solver, solver))
    ax.set_xlabel("training time (seconds)")
    ax.set_ylabel("exploitability (mbb/hand, log scale)")
    ax.set_title("Leduc poker: exploitability vs time")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)

    final = ", ".join(
        f"{s} final={float(srows[-1]['mbb_per_hand']):.4g}" for s, srows in by_solver.items()
    )
    print(f"plot_leduc: {len(rows)} pts, {final}, wrote {out}")


if __name__ == "__main__":
    main()
