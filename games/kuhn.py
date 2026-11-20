"""Kuhn poker: 3 cards (0=J,1=Q,2=K), ante 1, one bet of 1. Actions: 'p' (pass/check/fold), 'b' (bet/call)."""
from itertools import permutations

from games.base import Game

TERMINAL = {"pp", "bp", "bb", "pbp", "pbb"}


class KuhnPoker(Game):
    """State = (cards, history); cards is None until dealt, then (card_p0, card_p1)."""

    def initial_state(self):
        return (None, "")

    def is_terminal(self, state) -> bool:
        return state[1] in TERMINAL

    def is_chance(self, state) -> bool:
        return state[0] is None

    def chance_outcomes(self, state):
        deals = list(permutations(range(3), 2))
        return [(d, 1 / len(deals)) for d in deals]

    def current_player(self, state) -> int:
        return len(state[1]) % 2

    def legal_actions(self, state):
        return ["p", "b"]

    def next_state(self, state, action):
        cards, hist = state
        if cards is None:
            return (action, "")
        return (cards, hist + action)

    def utility(self, state, player: int) -> float:
        cards, hist = state
        if hist in ("bp", "pbp"):  # a fold: the bettor wins the 1 ante
            u0 = 1 if hist == "bp" else -1
        else:
            stake = 2 if "b" in hist else 1
            u0 = stake if cards[0] > cards[1] else -stake
        return u0 if player == 0 else -u0

    def infoset_key(self, state, player: int) -> str:
        return str(state[0][player]) + state[1]
