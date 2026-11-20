"""Phase 7 verification: play scripted CLI hands (both games, both seats) and check
(1) every bot probability shown equals the stored average strategy at that infoset (3 dp),
(2) the bot never hits an infoset missing from the stored strategy (no uniform fallback),
(3) each hand's chip result equals an independently computed payoff, and the running total is right.
Usage: python scripts/verify_phase7.py [--hands 40]. Prints one summary line."""
import argparse
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from agents.equilibrium import EquilibriumAgent  # noqa: E402
from play import cli  # noqa: E402

BETS = (2, 4)  # Leduc raise sizes per round, written out independently of games/leduc.py


def kuhn_payoff(h, me, opp, human_seat):
    """Human's chips from Kuhn history; me/opp are card ranks."""
    if h in ("bp", "pbp"):  # someone folded to a bet; folder is the player who acted last
        folder = (len(h) - 1) % 2
        return 1 if folder != human_seat else -1
    stake = 1 if h == "pp" else 2
    return stake if me > opp else -stake


def leduc_payoff(h, me, opp, board, human_seat):
    paid = [1, 1]
    for rnd, r in enumerate(h.split("/")):
        if not r:
            continue
        put = [0, 0]
        for i, a in enumerate(r):
            p = i % 2
            if a == "r":
                put[p] = put[1 - p] + BETS[rnd]
            elif a == "c":
                put[p] = put[1 - p]
            elif a == "f":
                folder = p
                paid = [paid[0] + put[0], paid[1] + put[1]]
                return paid[1 - human_seat] if folder != human_seat else -paid[human_seat]
        paid = [paid[0] + put[0], paid[1] + put[1]]
    mine, theirs = paid[human_seat], paid[1 - human_seat]
    if me == board and opp != board:
        return theirs
    if opp == board and me != board:
        return -mine
    if me == opp:
        return 0
    return theirs if me > opp else -mine


def check_game(name, hands, seed):
    strat = json.load(open(os.path.join(cli.STRAT_DIR, name + ".json")))
    bot_keys = []
    orig_act = EquilibriumAgent.act

    def act(self, game, state, infoset):
        bot_keys.append(infoset)
        return orig_act(self, game, state, infoset)

    EquilibriumAgent.act = act
    lines = []
    rng = np.random.default_rng(seed + 100)

    def inp(prompt):
        opts = re.findall(r"(\w)=", prompt)
        return str(rng.choice(opts))

    try:
        total = cli.run(name, seed=seed, hands=hands, inp=inp, out=lines.append)
    finally:
        EquilibriumAgent.act = orig_act

    ranks = cli.RANKS[name]
    rank = (lambda s: ranks.index(s[0]))
    prob_checks = chip_checks = 0
    errs = []
    ki = 0
    running = 0.0
    seat = me = board = None
    for ln in lines:
        if ln.startswith("--- Hand"):
            seat = int(re.search(r"player (\d)", ln).group(1))
            board = None
        elif ln.startswith("Your card: "):
            me = rank(ln.split(": ")[1])
        elif ln.startswith("Board: "):
            board = rank(ln.split(": ")[1])
        elif ln.startswith("Bot plays"):
            key = bot_keys[ki]
            ki += 1
            if key not in strat:
                errs.append("missing infoset " + key)
                continue
            shown = dict(re.findall(r"(\w)=([0-9.]+)", ln.split("here: ")[1]))
            dist = strat[key]
            z = sum(dist.get(a, 0.0) for a in shown)
            for a, v in shown.items():
                if abs(float(v) - round(dist.get(a, 0.0) / z, 3)) > 1e-9:
                    errs.append(f"{key} {a}: shown {v} stored {dist.get(a, 0.0) / z:.6f}")
                prob_checks += 1
        elif ln.startswith("History: "):
            hist = ln.split(": ")[1].split(".")[0]
            opp = rank(ln.split("Bot card: ")[1])
            exp = (kuhn_payoff(hist, me, opp, seat) if name == "kuhn"
                   else leduc_payoff(hist, me, opp, board, seat))
        elif ln.startswith("Result: "):
            r = float(re.search(r"Result: ([+-]?[0-9.]+)", ln).group(1))
            shown_total = float(ln.split("Running total: ")[1])
            running += exp
            if r != exp:
                errs.append(f"hand result {r} != expected {exp} ({hist})")
            if abs(shown_total - running) > 1e-9:
                errs.append(f"running total {shown_total} != {running}")
            chip_checks += 1
    if ki != len(bot_keys) or abs(total - running) > 1e-9:
        errs.append("bot move count or returned total mismatch")
    return prob_checks, chip_checks, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hands", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    summary, all_errs = [], []
    for g in ("kuhn", "leduc"):
        pc, cc, errs = check_game(g, a.hands, a.seed)
        summary.append(f"{g}: {pc} probs, {cc} hands")
        all_errs += [g + ": " + e for e in errs]
    status = "PASS" if not all_errs else "FAIL"
    print(f"verify_phase7 {status} ({'; '.join(summary)})" + ("" if not all_errs else " | " + all_errs[0]))
    sys.exit(0 if not all_errs else 1)


if __name__ == "__main__":
    main()
