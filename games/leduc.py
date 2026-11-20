"""Leduc poker: 6 cards (0..5; rank = card//2: J,Q,K), ante 1, bet 2 (round 1) / 4 (round 2),
max 2 raises per round, one public card after round 1, pair beats high card.
Actions: 'f' fold, 'c' check/call, 'r' raise. Player 0 acts first each round.
State = (cards, board, hist); cards None until dealt; hist rounds separated by '/'."""
from itertools import permutations

from games.base import Game

BET = (2, 4)
MAX_RAISES = 2


def _round_over(r: str) -> bool:
    return r.endswith("c") and len(r) >= 2


def _contributions(hist: str):
    """Chips each player has put in (ante included)."""
    total = [1, 1]
    for rnd, r in enumerate(hist.split("/")):
        put = [0, 0]
        for i, a in enumerate(r):
            p = i % 2
            if a == "r":
                put[p] = put[1 - p] + BET[rnd]
            elif a == "c":
                put[p] = put[1 - p]
        total[0] += put[0]
        total[1] += put[1]
    return total


class LeducPoker(Game):
    def initial_state(self):
        return (None, None, "")

    def is_terminal(self, state) -> bool:
        hist = state[2]
        if hist.endswith("f"):
            return True
        return "/" in hist and _round_over(hist.split("/")[-1])

    def is_chance(self, state) -> bool:
        cards, board, hist = state
        return cards is None or (board is None and hist.endswith("/"))

    def chance_outcomes(self, state):
        cards, board, hist = state
        if cards is None:
            deals = list(permutations(range(6), 2))
            return [(d, 1 / len(deals)) for d in deals]
        rest = [c for c in range(6) if c not in cards]
        return [(c, 1 / len(rest)) for c in rest]

    def _round(self, state) -> str:
        return state[2].split("/")[-1]

    def current_player(self, state) -> int:
        return len(self._round(state)) % 2

    def legal_actions(self, state):
        r = self._round(state)
        if r.endswith("r"):
            return ["f", "c", "r"] if r.count("r") < MAX_RAISES else ["f", "c"]
        return ["c", "r"]

    def next_state(self, state, action):
        cards, board, hist = state
        if cards is None:
            return (action, None, "")
        if board is None and hist.endswith("/"):
            return (cards, action, hist)
        hist += action
        if action != "f" and "/" not in hist and _round_over(hist):
            hist += "/"
        return (cards, board, hist)

    def utility(self, state, player: int) -> float:
        cards, board, hist = state
        c = _contributions(hist)
        if hist.endswith("f"):
            folder = (len(self._round(state)) - 1) % 2
            u0 = -c[0] if folder == 0 else c[1]
        else:
            r0, r1, rb = cards[0] // 2, cards[1] // 2, board // 2
            if r0 == rb and r1 != rb:
                u0 = c[1]
            elif r1 == rb and r0 != rb:
                u0 = -c[0]
            elif r0 == r1:
                u0 = 0
            else:
                u0 = c[1] if r0 > r1 else -c[0]
        return u0 if player == 0 else -u0

    def infoset_key(self, state, player: int) -> str:
        cards, board, hist = state
        b = "" if board is None else str(board // 2)
        return f"{cards[player] // 2}|{b}|{hist}"
