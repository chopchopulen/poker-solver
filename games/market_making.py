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
    """1-round market-making game. Player 0 = market maker (MM), player 1 = taker.

    State = (cards, noise, quote, act):
      cards = (mm_card, taker_card, hidden_card) or None before the deal;
      noise = True/False (taker is a noise trader) or None before that chance node;
      quote = index k = mid_idx * len(spreads) + spread_idx, or None before MM acts;
      act   = 'b' (taker buys), 's' (sells), 'p' (passes), or None.
    A noise trader's action is a uniform chance node, so the MM never sees the type.
    """

    def __init__(self, config: MMConfig | None = None):
        self.config = (config or MMConfig()).validate()
        if self.config.rounds != 1:
            raise NotImplementedError("rounds=2 not implemented yet (P9.6)")

    def initial_state(self):
        return (None, None, None, None)

    def is_terminal(self, state) -> bool:
        return state[3] is not None

    def is_chance(self, state) -> bool:
        cards, noise, quote, act = state
        if act is not None:
            return False
        return cards is None or noise is None or (quote is not None and noise)

    def chance_outcomes(self, state):
        cards, noise, _, _ = state
        if cards is None:
            deals = list(permutations(range(1, self.config.deck_size + 1), 3))
            return [(d, 1 / len(deals)) for d in deals]
        if noise is None:
            q = self.config.noise_prob
            return [(n, p) for n, p in ((True, q), (False, 1 - q)) if p > 0]
        return [(a, 1 / 3) for a in "bsp"]

    def current_player(self, state) -> int:
        return 0 if state[2] is None else 1

    def legal_actions(self, state):
        if state[2] is None:
            return list(range(len(self.config.mids) * len(self.config.spreads)))
        return ["b", "s", "p"]

    def quote(self, k: int):
        """Return (bid, ask) for quote index k."""
        mid = self.config.mids[k // len(self.config.spreads)]
        spread = self.config.spreads[k % len(self.config.spreads)]
        return mid - spread / 2, mid + spread / 2

    def next_state(self, state, action):
        cards, noise, quote, act = state
        if cards is None:
            return (action, None, None, None)
        if noise is None:
            return (cards, action, None, None)
        if quote is None:
            return (cards, noise, action, None)
        return (cards, noise, quote, action)

    def utility(self, state, player: int) -> float:
        cards, _, quote, act = state
        bid, ask = self.quote(quote)
        v = sum(cards)
        taker = {"b": v - ask, "s": bid - v, "p": 0}[act]
        return -taker if player == 0 else taker

    def infoset_key(self, state, player: int) -> str:
        cards, _, quote, _ = state
        if player == 0:
            return f"M{cards[0]}"
        see = self.config.taker_sees
        own = cards[1] if see >= 1 else "?"
        hid = cards[2] if see >= 2 else "?"
        return f"T{own}|{hid}|q{quote}"
