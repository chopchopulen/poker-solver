"""Vanilla CFR (full tree traversal) for two-player zero-sum extensive-form games."""
import numpy as np


class CFR:
    def __init__(self, game):
        self.game = game
        self.regret = {}     # key -> np.array of cumulative regrets
        self.strat_sum = {}  # key -> np.array of reach-weighted strategy sums
        self.actions = {}    # key -> list of legal actions

    def _strategy(self, key, n):
        r = np.maximum(self.regret[key], 0.0)
        s = r.sum()
        return r / s if s > 0 else np.full(n, 1.0 / n)

    def _walk(self, state, reach):
        """Return expected utility to player 0 at `state`. reach = [pi_0, pi_1, pi_chance]."""
        g = self.game
        if g.is_terminal(state):
            return g.utility(state, 0)
        if g.is_chance(state):
            v = 0.0
            for a, p in g.chance_outcomes(state):
                r = list(reach)
                r[2] *= p
                v += p * self._walk(g.next_state(state, a), r)
            return v
        pl = g.current_player(state)
        acts = g.legal_actions(state)
        n = len(acts)
        key = g.infoset_key(state, pl)
        if key not in self.regret:
            self.regret[key] = np.zeros(n)
            self.strat_sum[key] = np.zeros(n)
            self.actions[key] = list(acts)
        sigma = self._strategy(key, n)
        util = np.zeros(n)
        for i, a in enumerate(acts):
            r = list(reach)
            r[pl] *= sigma[i]
            util[i] = self._walk(g.next_state(state, a), r)
        node = float(sigma @ util)
        opp = 1 - pl
        sign = 1.0 if pl == 0 else -1.0  # util is from player 0's view
        cf = reach[opp] * reach[2]       # counterfactual reach: opponent * chance
        self.regret[key] += cf * sign * (util - node)
        self.strat_sum[key] += reach[pl] * sigma
        return node

    def train(self, iterations):
        for _ in range(iterations):
            self._walk(self.game.initial_state(), [1.0, 1.0, 1.0])

    def average_strategy(self):
        """key -> {action: prob}, from reach-weighted average (not current) strategy."""
        out = {}
        for key, s in self.strat_sum.items():
            t = s.sum()
            p = s / t if t > 0 else np.full(len(s), 1.0 / len(s))
            out[key] = dict(zip(self.actions[key], p))
        return out
