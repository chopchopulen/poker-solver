"""Save CFR+ average strategies to analysis/strategies/{kuhn,leduc}.json.
Usage: python scripts/save_strategies.py [--kuhn-iters N] [--leduc-iters N]"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from games.kuhn import KuhnPoker
from games.leduc import LeducPoker
from solvers.cfr_plus import CFRPlus


def save(game, iters, name):
    s = CFRPlus(game)
    s.train(iters)
    avg = {k: {str(a): float(p) for a, p in d.items()} for k, d in s.average_strategy().items()}
    path = os.path.join(ROOT, "analysis", "strategies", f"{name}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(avg, f, indent=1, sort_keys=True)
    print(f"{name}: {len(avg)} infosets, {iters} iters -> {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kuhn-iters", type=int, default=10000)
    ap.add_argument("--leduc-iters", type=int, default=2000)
    a = ap.parse_args()
    save(KuhnPoker(), a.kuhn_iters, "kuhn")
    save(LeducPoker(), a.leduc_iters, "leduc")
