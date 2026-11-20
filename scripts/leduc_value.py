"""Leduc game value for P1 (player 0) from the CFR+ average strategy.
Usage: python scripts/leduc_value.py [--iters N]   (prints one summary line)"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.leduc import LeducPoker
from solvers.cfr_plus import CFRPlus
from eval.best_response import best_response_value
from eval.game_value import game_value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=2000)
    n = ap.parse_args().iters
    g = LeducPoker()
    s = CFRPlus(g)
    s.train(n)
    avg = s.average_strategy()
    v = game_value(g, [avg, avg], 0)
    # certified bounds on the true game value v*: -BR_1(sigma_0) <= v* <= BR_0(sigma_1)
    lo = -best_response_value(g, [avg, avg], 1)
    hi = best_response_value(g, [avg, avg], 0)
    e = (hi - lo) / 2
    print(f"leduc cfr_plus iters={n} value_p1={v:.6f} bounds=[{lo:.6f},{hi:.6f}] expl={e:.2e} chips/hand")


if __name__ == "__main__":
    main()
