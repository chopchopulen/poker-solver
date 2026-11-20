"""Agent interface: picks an action at a decision state."""
from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def act(self, game, state, infoset):
        """Return a legal action at `state` given the acting player's infoset key."""

    def reset(self):
        """Clear per-match memory (default: stateless)."""
