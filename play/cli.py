"""Terminal play: human vs equilibrium bot. Bot's action probabilities shown after each bot move.
Usage: python -m play.cli --game kuhn|leduc --seed N [--hands H]. Seats alternate each hand."""
import argparse
import os

import numpy as np

from agents.equilibrium import EquilibriumAgent
from games.kuhn import KuhnPoker
from games.leduc import LeducPoker

GAMES = {"kuhn": KuhnPoker, "leduc": LeducPoker}
NAMES = {"kuhn": {"p": "pass/check/fold", "b": "bet/call"},
         "leduc": {"f": "fold", "c": "check/call", "r": "raise"}}
RANKS = {"kuhn": "JQK", "leduc": "JQK"}
STRAT_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis", "strategies")


def card_str(game_name, c):
    if game_name == "kuhn":
        return RANKS[game_name][c]
    return RANKS[game_name][c // 2] + "sh"[c % 2]  # suit tag distinguishes the two copies


def bot_probs(bot, game, state, infoset):
    """Probabilities the bot samples from at this infoset (uniform if unseen)."""
    legal = list(game.legal_actions(state))
    dist = bot.strategy.get(infoset)
    if dist is None:
        return {a: 1 / len(legal) for a in legal}
    p = np.array([dist.get(a, 0.0) for a in legal], dtype=float)
    p /= p.sum()
    return dict(zip(legal, p))


def play_hand(game_name, game, bot, human_seat, rng, inp, out):
    """Play one hand; returns human's chip result."""
    leduc = game_name == "leduc"
    s = game.initial_state()
    while not game.is_terminal(s):
        if game.is_chance(s):
            outs = game.chance_outcomes(s)
            dealing = s[0] is None
            s = game.next_state(s, outs[rng.choice(len(outs), p=[p for _, p in outs])][0])
            if dealing:
                out("Your card: " + card_str(game_name, s[0][human_seat]))
            elif leduc:
                out("Board: " + card_str(game_name, s[1]))
            continue
        p = game.current_player(s)
        legal = list(game.legal_actions(s))
        key = game.infoset_key(s, p)
        if p == human_seat:
            opts = ", ".join(a + "=" + NAMES[game_name][a] for a in legal)
            while True:
                ans = inp("Your move (" + opts + "): ").strip().lower()
                if ans in legal:
                    break
                out("Invalid input '" + ans + "'.")
            a = ans
        else:
            a = bot.act(game, s, key)
            pr = bot_probs(bot, game, s, key)
            out("Bot plays " + a + ". Its strategy here: "
                + ", ".join(k + "=" + format(v, ".3f") for k, v in pr.items()))
        s = game.next_state(s, a)
    hist = s[2] if leduc else s[1]
    out("History: " + hist + ". Bot card: " + card_str(game_name, s[0][1 - human_seat]))
    return game.utility(s, human_seat)


def run(game_name, seed=0, hands=1, inp=input, out=print):
    game = GAMES[game_name]()
    bot = EquilibriumAgent.from_json(os.path.join(STRAT_DIR, game_name + ".json"), seed)
    rng = np.random.default_rng(seed)
    total = 0.0
    for h in range(hands):
        seat = h % 2
        out("--- Hand " + str(h + 1) + " (you are player " + str(seat) + ") ---")
        r = play_hand(game_name, game, bot, seat, rng, inp, out)
        total += r
        out("Result: " + format(r, "+g") + " chips. Running total: " + format(total, "+g"))
    return total


def main(argv=None):
    ap = argparse.ArgumentParser(description="Play Kuhn or Leduc poker against the equilibrium bot.")
    ap.add_argument("--game", choices=list(GAMES), default="kuhn")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--hands", type=int, default=1)
    a = ap.parse_args(argv)
    run(a.game, a.seed, a.hands)


if __name__ == "__main__":
    main()
