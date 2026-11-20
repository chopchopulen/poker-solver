"""Phase 5 verification checks. Usage: python scripts/verify_phase5.py
1. Exact exploiter EV (from best_response) == game_value of its pure policy vs each bot.
2. Every exact EV in analysis/bot_matches.csv lies in its simulated 95% CI.
3. Mirroring: same chance seed -> identical cards in both seatings.
4. CI coverage: fraction of independent small matches whose 95% CI covers the exact EV."""
import csv
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.base import Agent
from agents.bots import BOTS
from agents.exploiter import Exploiter, bot_strategy
from eval.game_value import game_value
from eval.match import play_match
from games.leduc import LeducPoker
from tests.test_equilibrium_agent import decision_states


def chance_trace(game, seed, actions):
    """Cards dealt with a given chance seed when players follow a fixed action list."""
    rng = np.random.default_rng(seed)
    s, i, out = game.initial_state(), 0, []
    while not game.is_terminal(s):
        if game.is_chance(s):
            outs = game.chance_outcomes(s)
            a = outs[rng.choice(len(outs), p=[p for _, p in outs])][0]
            out.append(a)
        else:
            legal = list(game.legal_actions(s))
            a = actions[i % len(actions)] if actions[i % len(actions)] in legal else legal[0]
            i += 1
        s = game.next_state(s, a)
    return out


def main():
    g = LeducPoker()
    states = decision_states(g)
    fails = []
    # 1. BR value consistency
    max_gap = 0.0
    bots = {}
    for name, cls in BOTS.items():
        bot = cls(0) if name == "random" else cls()
        bs = bot_strategy(g, bot, states)
        bots[name] = (bot, bs)
        for seat in (0, 1):
            ex = Exploiter(g, bs, seat)
            pol = {}
            for s in states:
                if g.current_player(s) == seat:
                    k = g.infoset_key(s, seat)
                    legal = list(g.legal_actions(s))
                    a = ex.best.get(k, legal[0])
                    pol[k] = {x: float(x == a) for x in legal}
            st = [None, None]
            st[seat], st[1 - seat] = pol, bs
            max_gap = max(max_gap, abs(game_value(g, st, seat) - ex.value))
    if max_gap > 1e-9:
        fails.append(f"BR value gap {max_gap:.2e}")
    # 2. csv exact inside CI
    with open(os.path.join(ROOT, "analysis", "bot_matches.csv")) as f:
        rows = list(csv.DictReader(f))
    outside = [r for r in rows if not float(r["lo_mbb"]) <= float(r["exact_mbb"]) <= float(r["hi_mbb"])]
    if len(rows) != 8 or outside:
        fails.append(f"csv rows={len(rows)} outside_ci={len(outside)}")
    # 3. mirroring: chance outcomes independent of the actions taken
    for seed in range(200):
        a = chance_trace(g, seed, ["c"])
        b = chance_trace(g, seed, ["r", "c"])
        if a[0] != b[0] or (len(a) > 1 and len(b) > 1 and a[1] != b[1]):
            fails.append(f"mirror mismatch seed {seed}")
            break
    # 4. CI coverage: exploiter (seat-dispatching) vs random bot, 100 matches x 1000 pairs
    bot, bs = bots["random"]
    exs = [Exploiter(g, bs, s) for s in (0, 1)]
    exact = 0.5 * (exs[0].value + exs[1].value)

    class Both(Agent):
        def act(self, game, state, infoset):
            return exs[game.current_player(state)].act(game, state, infoset)

    n_runs, covered = 100, 0
    for k in range(n_runs):
        bot.seed = 1000 + k
        r = play_match(g, Both(), bot, 1000, seed=1000 + k)
        covered += (r["mean"] - r["ci"]) <= exact <= (r["mean"] + r["ci"])
    cov = covered / n_runs
    if not 0.88 <= cov <= 1.0:
        fails.append(f"coverage {cov:.2f}")
    status = "PASS" if not fails else "FAIL " + "; ".join(fails)
    print(f"phase5 verify: br_gap={max_gap:.1e} csv_rows={len(rows)} outside_ci={len(outside)} "
          f"ci_coverage={cov:.2f} (100x1000 pairs) -> {status}")


if __name__ == "__main__":
    main()
