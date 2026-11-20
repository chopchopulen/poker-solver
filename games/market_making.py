"""Market-making card game (Phase 9): config + 1-round game.

Cards 1..deck_size dealt without replacement: MM card, taker card, hidden card.
V = sum of the 3 cards. MM quotes (mid, spread) -> bid = mid - s/2, ask = mid + s/2.
Taker sees the quote and picks buy / sell / pass. Zero-sum, 1 unit.
"""
from dataclasses import dataclass
from itertools import permutations

from games.base import Game


@dataclass
class MMConfig:
    deck_size: int = 10
    mids: tuple = (8, 11, 14, 17, 20)
    spreads: tuple = (1, 2, 4)
    taker_sees: int = 1  # 0 = nothing, 1 = own card, 2 = own + hidden card
    noise_prob: float = 0.25  # chance taker is a noise trader (buy/sell/pass uniform)
    rounds: int = 1  # 1 or 2 quote/taker rounds

    def validate(self) -> "MMConfig":
        if self.deck_size < 3:
            raise ValueError(f"deck_size must be >= 3, got {self.deck_size}")
        if self.taker_sees not in (0, 1, 2):
            raise ValueError(f"taker_sees must be in {{0,1,2}}, got {self.taker_sees}")
        if self.rounds not in (1, 2):
            raise ValueError(f"rounds must be in {{1,2}}, got {self.rounds}")
        if not self.mids:
            raise ValueError("mids must be non-empty")
        if not self.spreads or any(s <= 0 for s in self.spreads):
            raise ValueError(f"spreads must be non-empty and > 0, got {self.spreads}")
        if not (0.0 <= self.noise_prob <= 1.0):
            raise ValueError(f"noise_prob must be in [0,1], got {self.noise_prob}")
        return self


class MarketMakingGame(Game):
    """Market-making game, 1 or 2 rounds. Player 0 = market maker (MM), player 1 = taker.

    State = (cards, noise, q1, a1, q2, a2):
      cards = (mm_card, taker_card, hidden_card) or None before the deal;
      noise = True/False (taker is a noise trader, fixed for both rounds) or None;
      q = index k = mid_idx * len(spreads) + spread_idx, or None before MM acts;
      a = 'b' (taker buys), 's' (sells), 'p' (passes), or None.
    A noise trader's action is a uniform chance node, so the MM never sees the type.
    rounds=2: MM requotes after seeing a1; payoff is the sum of both trades (V is fixed).
    """

    def __init__(self, config: MMConfig | None = None):
        self.config = (config or MMConfig()).validate()

    def initial_state(self):
        return (None,) * 6

    def _last(self) -> int:
        return 3 if self.config.rounds == 1 else 5

    def is_terminal(self, state) -> bool:
        return state[self._last()] is not None

    def is_chance(self, state) -> bool:
        if self.is_terminal(state):
            return False
        if state[0] is None or state[1] is None:
            return True
        return bool(state[1]) and self._pending_action(state)

    @staticmethod
    def _pending_action(state) -> bool:
        """True if a quote was posted and the taker has not yet acted on it."""
        return (state[2] is not None and state[3] is None) or (state[4] is not None and state[5] is None)

    def chance_outcomes(self, state):
        if state[0] is None:
            deals = list(permutations(range(1, self.config.deck_size + 1), 3))
            return [(d, 1 / len(deals)) for d in deals]
        if state[1] is None:
            q = self.config.noise_prob
            return [(n, p) for n, p in ((True, q), (False, 1 - q)) if p > 0]
        return [(a, 1 / 3) for a in "bsp"]

    def current_player(self, state) -> int:
        return 1 if self._pending_action(state) else 0

    def legal_actions(self, state):
        if self._pending_action(state):
            return ["b", "s", "p"]
        return list(range(len(self.config.mids) * len(self.config.spreads)))

    def quote(self, k: int):
        """Return (bid, ask) for quote index k."""
        mid = self.config.mids[k // len(self.config.spreads)]
        spread = self.config.spreads[k % len(self.config.spreads)]
        return mid - spread / 2, mid + spread / 2

    def next_state(self, state, action):
        i = state.index(None)  # slots fill in order: cards, noise, q1, a1, q2, a2
        return state[:i] + (action,) + state[i + 1:]

    def utility(self, state, player: int) -> float:
        cards = state[0]
        v = sum(cards)
        taker = 0.0
        for q, a in ((state[2], state[3]), (state[4], state[5])):
            if a is None:
                continue
            bid, ask = self.quote(q)
            taker += {"b": v - ask, "s": bid - v, "p": 0}[a]
        return -taker if player == 0 else taker

    def infoset_key(self, state, player: int) -> str:
        cards, _, q1, a1, q2, _ = state
        r2 = q2 is not None or (q1 is not None and a1 is not None)  # round-2 decision node
        if player == 0:
            return f"M{cards[0]}|q{q1}|{a1}" if r2 else f"M{cards[0]}"
        see = self.config.taker_sees
        own = cards[1] if see >= 1 else "?"
        hid = cards[2] if see >= 2 else "?"
        key = f"T{own}|{hid}|q{q1}"
        return f"{key}|{a1}|q{q2}" if r2 else key
