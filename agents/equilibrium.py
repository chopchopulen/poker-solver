"""Plays by sampling from a stored average strategy: key -> {action: prob}."""
import json

import numpy as np

from agents.base import Agent


class EquilibriumAgent(Agent):
    def __init__(self, strategy, seed=0):
        self.strategy = strategy
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    @classmethod
    def from_json(cls, path, seed=0):
        with open(path) as f:
            return cls(json.load(f), seed)

    def reset(self):
        self.rng = np.random.default_rng(self.seed)

    def act(self, game, state, infoset):
        legal = list(game.legal_actions(state))
        dist = self.strategy.get(infoset)
        if dist is None:
            return legal[self.rng.integers(len(legal))]  # unseen infoset: uniform
        p = np.array([dist.get(a, 0.0) for a in legal], dtype=float)
        p = p / p.sum()
        return legal[self.rng.choice(len(legal), p=p)]
