"""Market-making card game (Phase 9). Scaffold only: config + stub game.

Cards 1..deck_size dealt without replacement: MM card, taker card, hidden card.
V = sum of the 3 cards. MM quotes (mid, spread) -> bid = mid - s/2, ask = mid + s/2.
Taker sees the quote and picks buy / sell / pass. Zero-sum, 1 unit.
"""
from dataclasses import dataclass

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
    """Stub. Implemented in P9.2."""

    def __init__(self, config: MMConfig | None = None):
        self.config = (config or MMConfig()).validate()

    def initial_state(self):
        raise NotImplementedError

    def is_terminal(self, state) -> bool:
        raise NotImplementedError

    def is_chance(self, state) -> bool:
        raise NotImplementedError

    def chance_outcomes(self, state):
        raise NotImplementedError

    def current_player(self, state) -> int:
        raise NotImplementedError

    def legal_actions(self, state):
        raise NotImplementedError

    def next_state(self, state, action):
        raise NotImplementedError

    def utility(self, state, player: int) -> float:
        raise NotImplementedError

    def infoset_key(self, state, player: int) -> str:
        raise NotImplementedError
