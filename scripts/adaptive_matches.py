"""Adaptive agent (cap 1.0 and safe cap 0.2) vs each Leduc bot and vs equilibrium, mirrored matches, 95% CI.
Appends reference equilibrium/exploiter rows from analysis/bot_matches.csv.
Writes analysis/adaptive_matches.csv. Usage: python scripts/adaptive_matches.py [--pairs N] [--seed S]"""
import argparse
import csv
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.adaptive import AdaptiveAgent
from agents.bots import BOTS
from agents.equilibrium import EquilibriumAgent
from eval.match import play_match
from games.leduc import LeducPoker

FIELDS = ["agent", "bot", "n_hands", "mbb_per_hand", "ci95_mbb", "lo_mbb", "hi_mbb"]


def main(pairs, seed):
    g = LeducPoker()
    eq_path = os.path.join(ROOT, "analysis", "strategies", "leduc.json")
    eq = EquilibriumAgent.from_json(eq_path, seed=seed)
    rows = []
    opps = []
    for n, c in BOTS.items():
        opps.append((n, c, seed if n == "random" else None))
    for cap in (1.0, 0.2):
        label = f"adaptive_cap{cap}"
        for name, cls, arg in opps + [("equilibrium", None, None)]:
            t0 = time.time()
            if cls is None:
                opp = EquilibriumAgent.from_json(eq_path, seed=seed + 1)
            else:
                opp = cls(arg) if arg is not None else cls()
            ag = AdaptiveAgent(g, eq.strategy, seed=seed, cap=cap)
            r = play_match(g, ag, opp, pairs, seed=seed)
            rows.append({"agent": label, "bot": name, "n_hands": r["n_hands"],
                         "mbb_per_hand": round(r["mbb"], 2), "ci95_mbb": round(r["ci_mbb"], 2),
                         "lo_mbb": round(r["lo_mbb"], 2), "hi_mbb": round(r["hi_mbb"], 2)})
            print(f"{label} vs {name}: {r['mbb']:.1f} +/- {r['ci_mbb']:.1f} [{time.time() - t0:.0f}s]", file=sys.stderr)
    with open(os.path.join(ROOT, "analysis", "bot_matches.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({k: r[k] for k in FIELDS})  # reference rows: equilibrium, exploiter
    out = os.path.join(ROOT, "analysis", "adaptive_matches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}: {len(rows)} rows")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    main(a.pairs, a.seed)
