"""Avg MM quote per MM card vs exact E[V | mm_card], from analysis/mm_game_strategy.csv (default config).
Usage: python scripts/mm_quotes.py   (run scripts/mm_solve.py first)"""
import csv
import os
import sys
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from games.market_making import MMConfig

cfg = MMConfig()
N, ns = cfg.deck_size, len(cfg.spreads)
strat = {}
with open("analysis/mm_game_strategy.csv") as f:
    for r in csv.DictReader(f):
        if r["infoset"].startswith("M"):
            strat.setdefault(int(r["infoset"][1:]), {})[int(r["action"])] = float(r["prob"])

rows = []
for c in range(1, N + 1):
    p = strat[c]
    mid = sum(q * cfg.mids[k // ns] for k, q in p.items())
    spr = sum(q * cfg.spreads[k % ns] for k, q in p.items())
    vs = [sum(d) for d in permutations(range(1, N + 1), 3) if d[0] == c]
    rows.append((c, mid, spr, sum(vs) / len(vs)))
with open("analysis/mm_game_quotes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mm_card", "avg_mid", "avg_spread", "E_V_given_mm_card"])
    w.writerows([(c, f"{m:.4f}", f"{s:.4f}", f"{e:.4f}") for c, m, s, e in rows])
plt.figure(figsize=(5, 4))
ev = [r[3] for r in rows]
plt.plot(ev, ev, "k--", label="y = x")
plt.plot(ev, [r[1] for r in rows], "o-", label="avg mid")
plt.xlabel("E[V | MM card]"); plt.ylabel("avg mid"); plt.legend(); plt.tight_layout()
plt.savefig("analysis/mm_game_quotes.png", dpi=120)
dev = max(abs(m - e) for _, m, _, e in rows)
print(f"mm_quotes: max|avg_mid-E[V|card]|={dev:.3f} (mid grid {cfg.mids}) -> analysis/mm_game_quotes.csv/png")
