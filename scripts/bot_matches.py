"""Equilibrium and exploiter vs each Leduc bot, mirrored matches with 95% CI.
Writes analysis/bot_matches.csv. Usage: python scripts/bot_matches.py [--pairs N] [--seed S]"""
import argparse
import csv
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.base import Agent
from agents.bots import BOTS
from agents.equilibrium import EquilibriumAgent
from agents.exploiter import Exploiter, bot_strategy
from eval.game_value import game_value
from eval.match import play_match
from games.leduc import LeducPoker
from tests.test_equilibrium_agent import decision_states


class BothSeats(Agent):
    """Dispatches to the per-seat exploiter by whoever is to act."""

    def __init__(self, ex):
        self.ex = ex

    def act(self, game, state, infoset):
        return self.ex[game.current_player(state)].act(game, state, infoset)


def main(pairs, seed):
    g = LeducPoker()
    states = decision_states(g)
    eq_path = os.path.join(ROOT, "analysis", "strategies", "leduc.json")
    eq = EquilibriumAgent.from_json(eq_path, seed=seed)
    rows = []
    for name, cls in BOTS.items():
        t0 = time.time()
        bot = cls(seed) if name == "random" else cls()
        bs = bot_strategy(g, bot, states)
        exs = [Exploiter(g, bs, s) for s in (0, 1)]
        # exact EV (chips/hand, seat-averaged) of each agent vs this bot
        exact_br = 0.5 * (exs[0].value + exs[1].value)
        exact_eq = 0.0
        for seat in (0, 1):
            st = [None, None]
            st[seat], st[1 - seat] = eq.strategy, bs
            exact_eq += 0.5 * game_value(g, st, seat)
        for label, agent, exact in (("equilibrium", eq, exact_eq), ("exploiter", BothSeats(exs), exact_br)):
            r = play_match(g, agent, bot, pairs, seed=seed)
            rows.append({"agent": label, "bot": name, "n_hands": r["n_hands"],
                         "mbb_per_hand": round(r["mbb"], 2), "ci95_mbb": round(r["ci_mbb"], 2),
                         "lo_mbb": round(r["lo_mbb"], 2), "hi_mbb": round(r["hi_mbb"], 2),
                         "exact_mbb": round(1000 * exact, 2)})
            print(f"{label} vs {name}: {r['mbb']:.1f} +/- {r['ci_mbb']:.1f} mbb/hand (exact {1000 * exact:.1f})")
        print(f"  [{name} {time.time() - t0:.0f}s]", file=sys.stderr)
    out = os.path.join(ROOT, "analysis", "bot_matches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}: {len(rows)} rows, {2 * pairs} hands each")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    main(a.pairs, a.seed)
