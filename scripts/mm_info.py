"""Sweep taker_sees in {0,1,2} x noise levels: avg spread, trade rate, MM EV (total / vs informed / vs noise flow), exploitability.
Usage: python scripts/mm_info.py [--iters 1000] [--noises 0.25,0.5] [--deck 10]"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from games.market_making import MMConfig
from scripts.mm_solve import solve


def stats(g, avg):
    """Exact traversal under avg strategy (both players). Returns MM-perspective stats."""
    spread = 0.0
    ev, wt, tr = [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]  # index 0 = informed taker, 1 = noise trader
    ns = len(g.config.spreads)

    def probs(s, p, acts):
        d = avg.get(g.infoset_key(s, p))
        return [(a, (d.get(a, 0.0) if d else 1 / len(acts))) for a in acts]

    def rec(s, w):
        nonlocal spread
        if g.is_terminal(s):
            i = 1 if s[1] else 0
            ev[i] += w * g.utility(s, 0)
            wt[i] += w
            tr[i] += w * (s[3] != "p")
            return
        if g.is_chance(s):
            for a, p in g.chance_outcomes(s):
                rec(g.next_state(s, a), w * p)
            return
        p = g.current_player(s)
        for a, q in probs(s, p, g.legal_actions(s)):
            if q <= 0:
                continue
            if p == 0:
                spread += w * q * g.config.spreads[a % ns]
            rec(g.next_state(s, a), w * q)

    rec(g.initial_state(), 1.0)
    tw = wt[0] + wt[1]
    nan = float("nan")
    return dict(avg_spread=spread / tw,
                trade_rate=(tr[0] + tr[1]) / tw,
                mm_ev=(ev[0] + ev[1]) / tw,
                mm_ev_informed=ev[0] / wt[0] if wt[0] else nan,
                mm_ev_noise=ev[1] / wt[1] if wt[1] else nan)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--noises", default="0.25,0.5")
    ap.add_argument("--deck", type=int, default=10)
    a = ap.parse_args()
    rows = []
    for noise in [float(x) for x in a.noises.split(",")]:
        for sees in (0, 1, 2):
            cfg = MMConfig(deck_size=a.deck, taker_sees=sees, noise_prob=noise)
            g, avg, conv = solve(cfg, a.iters)
            r = dict(taker_sees=sees, noise=noise, **stats(g, avg), exploitability=conv[-1][2])
            rows.append(r)
            print(f"sees={sees} noise={noise} " + " ".join(
                f"{k}={v:.4g}" for k, v in r.items() if k not in ("taker_sees", "noise")), flush=True)
    cols = list(rows[0])
    os.makedirs("analysis", exist_ok=True)
    with open("analysis/mm_game_info.csv", "w", newline="") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    for noise in sorted({r["noise"] for r in rows}):
        rr = [r for r in rows if r["noise"] == noise]
        x = [r["taker_sees"] for r in rr]
        ax[0].plot(x, [r["avg_spread"] for r in rr], "o-", label=f"noise={noise}")
        ax[1].plot(x, [r["trade_rate"] for r in rr], "o-", label=f"noise={noise}")
        ax[2].plot(x, [r["mm_ev"] for r in rr], "o-", label=f"total, noise={noise}")
        ax[2].plot(x, [r["mm_ev_informed"] for r in rr], "s--", label=f"vs informed, noise={noise}")
        ax[2].plot(x, [r["mm_ev_noise"] for r in rr], "^:", label=f"vs noise, noise={noise}")
    for i, t in enumerate(["avg spread", "trade rate", "MM EV"]):
        ax[i].set_xlabel("taker_sees")
        ax[i].set_title(t)
        ax[i].set_xticks([0, 1, 2])
    ax[0].legend()
    ax[2].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig("analysis/mm_game_info.png", dpi=120)
    print(f"mm_info: {len(rows)} configs, max expl={max(r['exploitability'] for r in rows):.3g} -> analysis/mm_game_info.csv/png")
