"""Fixed-rule Leduc bots. Actions: 'f' fold, 'c' check/call, 'r' raise.
Infoset key = "<rank>|<board rank or empty>|<hist>" (see games/leduc.py)."""
import numpy as np

from agents.base import Agent


class AlwaysCall(Agent):
    def act(self, game, state, infoset):
        return "c"


class AlwaysRaise(Agent):
    def act(self, game, state, infoset):
        return "r" if "r" in game.legal_actions(state) else "c"  # capped: call


class Tight(Agent):
    """Strong = King, or pair with the board. Strong: raise if possible else call.
    Weak: fold to a bet, otherwise check."""

    @staticmethod
    def is_strong(infoset):
        rank, board, _ = infoset.split("|")
        return rank == "2" or rank == board

    def act(self, game, state, infoset):
        legal = game.legal_actions(state)
        if self.is_strong(infoset):
            return "r" if "r" in legal else "c"
        return "f" if "f" in legal else "c"


class RandomBot(Agent):
    def __init__(self, seed=0):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def reset(self):
        self.rng = np.random.default_rng(self.seed)

    def act(self, game, state, infoset):
        legal = list(game.legal_actions(state))
        return legal[self.rng.integers(len(legal))]


BOTS = {"always_call": AlwaysCall, "always_raise": AlwaysRaise, "tight": Tight, "random": RandomBot}
