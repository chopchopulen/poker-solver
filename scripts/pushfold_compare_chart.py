"""Compare our push/fold equilibrium (analysis/pushfold_ranges.csv) with a published HU Nash chart.

Source: PokerStrategy.com, "Nash Ranges for the Push-or-Fold Play", Table 1 (without ante),
https://www.pokerstrategy.com/strategy/sit-and-go/1779/ (accessed 2026-11-20). ES = smaller stack
before blinds, in BB (same as our S). Range strings below are copied verbatim (NPR = SB push, NCR = BB call).
A hand counts as "in" our range if its probability >= 0.5. EV edge = action value - fold value, in BB,
for that hand vs the opponent's equilibrium strategy.
Usage: python scripts/pushfold_compare_chart.py -> analysis/pushfold_chart_compare.csv + one summary line."""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solvers.pushfold import bb_values, sb_values  # noqa: E402
from games.holdem_classes import HAND_CLASSES, class_combos  # noqa: E402
R = "23456789TJQKA"
SRC = {  # verbatim, pokerstrategy.com/strategy/sit-and-go/1779/ Table 1 (without ante)
 9: ("22+, Kx+, Q2s+, Q5o+, J2s+, J8o+, T5s+, T8o+, 95s+, 97o+, 85s+, 87o, 74s+, 64s+, 53s+",
     "22+, Ax+, K2s+, K4o+, Q4s+, Q8o+, J7s+, J9o+, T8s+, T9o, 98s"),
 10: ("22+, Kx+, Q2s+, Q7o+, J3s+, J8o+, T5s+, T8o+, 95s+, 97o+, 85s+, 87o, 74s+, 64s+, 53s+",
      "22+, Ax+, K2s+, K6o+, Q6s+, Q8o+, J8s+, J9o+, T9s"),
 11: ("22+, Kx+, Q2s+, Q8o+, J4s+, J8o+, T5s+, T8o+, 95s+, 98o, 85s+, 87o, 74s+, 64s+, 53s+",
      "22+, Ax+, K2s+, K6o+, Q7s+, Q9o+, J8s+, JTo, T9s"),
}
def expand(s):
    out = set()
    for t in [x.strip() for x in s.split(",") if x.strip()]:
        plus = t.endswith("+"); t = t.rstrip("+")
        if t[0] == t[1]:                       # pairs
            out |= {r + r for r in R[R.index(t[0]):]} if plus else {t}
        elif t[1] == "x":                      # Kx+ = every hand with top card >= K
            for h in HAND_CLASSES:
                if R.index(h[0]) >= R.index(t[0]) : out.add(h)
        else:
            hi, lo, k = t[0], t[1], t[2]
            los = R[R.index(lo):R.index(hi)] if plus else lo
            out |= {hi + l + k for l in los}
    return out


def main():
    d = np.load("analysis/pushfold_equity.npz")
    eq, w = d["eq"], d["w"]
    labels = [str(x) for x in d["labels"]]
    combos = {h: len(class_combos(h)) for h in HAND_CLASSES}
    rows = list(csv.DictReader(open("analysis/pushfold_ranges.csv")))
    psb, pbb = w.sum(1) / w.sum(), w.sum(0) / w.sum()
    out, tot, ndis, maxedge = [], {"shove": 0, "call": 0}, {"shove": 0, "call": 0}, 0.0
    for S, (npr, ncr) in SRC.items():
        st = {r["hand"]: (float(r["shove"]), float(r["call"])) for r in rows if int(r["stack"]) == S}
        s = np.array([st[h][0] for h in labels])
        c = np.array([st[h][1] for h in labels])
        sv, fv = sb_values(eq, w, S, c)
        cv, bf = bb_values(eq, w, S, s)
        for name, rng, col in (("shove", expand(npr), 0), ("call", expand(ncr), 1)):
            assert rng <= set(HAND_CLASSES), rng - set(HAND_CLASSES)
            for i, h in enumerate(labels):
                ours = st[h][col]
                edge = (sv[i] - fv[i]) / psb[i] if col == 0 else (cv[i] - bf[i]) / pbb[i]
                differ = (ours >= 0.5) != (h in rng)
                tot[name] += 1
                ndis[name] += differ
                if differ:
                    maxedge = max(maxedge, abs(edge))
                out.append((S, name, h, int(h in rng), f"{ours:.6f}", int(differ), f"{edge:+.5f}"))
            pct = 100 * sum(combos[h] for h in rng) / 1326
            print(f"S={S} {name}: chart {pct:.1f}% of combos", file=sys.stderr)
    with open("analysis/pushfold_chart_compare.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["stack", "action", "hand", "chart_in_range", "our_prob", "differ", "ev_edge_bb"])
        wr.writerows(out)
    agree = 1 - (ndis["shove"] + ndis["call"]) / (tot["shove"] + tot["call"])
    print(f"chart compare S=9-11: shove {ndis['shove']}/{tot['shove']} differ, call {ndis['call']}/{tot['call']} differ, "
          f"agree {100 * agree:.1f}%, max |EV edge| of disagreements {maxedge:.3f} BB")


if __name__ == "__main__":
    main()
