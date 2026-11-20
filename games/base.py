"""Abstract interface for extensive-form, two-player zero-sum games with chance."""
from abc import ABC, abstractmethod


class Game(ABC):
    """Extensive-form game. States are opaque, immutable objects."""

    @abstractmethod
    def initial_state(self):
        """Return the root state (before any chance outcome or action)."""

    @abstractmethod
    def is_terminal(self, state) -> bool:
        """True if no further actions or chance events occur at `state`."""

    @abstractmethod
    def is_chance(self, state) -> bool:
        """True if nature acts at `state` (e.g. dealing cards)."""

    @abstractmethod
    def chance_outcomes(self, state):
        """Return list of (action, probability) at a chance node; probs sum to 1."""

    @abstractmethod
    def current_player(self, state) -> int:
        """Return the player (0 or 1) to act at a non-terminal, non-chance state."""

    @abstractmethod
    def legal_actions(self, state):
        """Return list of legal actions for the acting player at `state`."""

    @abstractmethod
    def next_state(self, state, action):
        """Return the state reached by applying `action` (player or chance)."""

    @abstractmethod
    def utility(self, state, player: int) -> float:
        """Return terminal payoff to `player` at a terminal `state`."""

    @abstractmethod
    def infoset_key(self, state, player: int) -> str:
        """Return key of `player`'s information set: only what that player can see."""
