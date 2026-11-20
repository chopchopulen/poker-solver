"""2-round market-making: MM requotes after seeing taker's round-1 action.
Writes analysis/mm_game_2round.csv: round-1 avg mid vs round-2 avg mid after buy/sell/pass.
Usage: python scripts/mm_2round.py [--deck 6] [--iters 1000] [--noise 0.25] [--taker-sees 1]"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.market_making import MMConfig
from scripts.mm_solve import solve

MIDS, SPREADS = (8, 11, 14), (2, 4)


def quote_stats(d, cfg):
    ns = len(cfg.spreads)
    mid = sum(p * cfg.mids[int(a) // ns] for a, p in d.items())
    spr = sum(p * cfg.spreads[int(a) % ns] for a, p in d.items())
    return mid, spr


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", type=int, default=6)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--noise", type=float, default=0.25)
    ap.add_argument("--taker-sees", type=int, default=1)
    a = ap.parse_args()
    cfg = MMConfig(deck_size=a.deck, mids=MIDS, spreads=SPREADS, taker_sees=a.taker_sees,
                   noise_prob=a.noise, rounds=2)
    g, avg, rows = solve(cfg, a.iters, npoints=8)
    out = []
    for card in range(1, a.deck + 1):
        r1 = quote_stats(avg[f"M{card}"], cfg)
        row = {"mm_card": card, "r1_mid": round(r1[0], 4), "r1_spread": round(r1[1], 4)}
        for act, name in (("b", "buy"), ("s", "sell"), ("p", "pass")):
            # unweighted mean over round-1 quotes (the infosets differ by q1)
            qs = [quote_stats(d, cfg) for k, d in avg.items()
                  if k.startswith(f"M{card}|q") and k.endswith(f"|{act}")]
            row[f"r2_mid_{name}"] = round(sum(m for m, _ in qs) / len(qs), 4)
            row[f"r2_spread_{name}"] = round(sum(s for _, s in qs) / len(qs), 4)
        out.append(row)
    os.makedirs("analysis", exist_ok=True)
    with open("analysis/mm_game_2round.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"mm_2round: deck={a.deck} sees={a.taker_sees} noise={a.noise} iters={rows[-1][0]} "
          f"expl={rows[-1][2]:.3g} {rows[-1][1]:.1f}s infosets={len(avg)} -> analysis/mm_game_2round.csv")
