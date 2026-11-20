"""External-sampling MCCFR (Lanctot et al. 2009) for two-player zero-sum games."""
import numpy as np


class MCCFR:
    def __init__(self, game, seed=0):
        self.game = game
        self.rng = np.random.default_rng(seed)
        self.regret = {}
        self.strat_sum = {}
        self.actions = {}
        self._register(game.initial_state())  # so unvisited infosets default to uniform

    def _register(self, state):
        g = self.game
        if g.is_terminal(state):
            return
        if g.is_chance(state):
            for a, _ in g.chance_outcomes(state):
                self._register(g.next_state(state, a))
            return
        acts = g.legal_actions(state)
        key = g.infoset_key(state, g.current_player(state))
        if key not in self.regret:
            self.regret[key] = np.zeros(len(acts))
            self.strat_sum[key] = np.zeros(len(acts))
            self.actions[key] = list(acts)
        for a in acts:
            self._register(g.next_state(state, a))

    def _strategy(self, key, n):
        r = np.maximum(self.regret[key], 0.0)
        s = r.sum()
        return r / s if s > 0 else np.full(n, 1.0 / n)

    def _walk(self, state, trav):
        """Sampled value for player `trav`. Chance + opponent sampled, traverser enumerated."""
        g = self.game
        if g.is_terminal(state):
            return g.utility(state, trav)
        if g.is_chance(state):
            outs = g.chance_outcomes(state)
            i = self.rng.choice(len(outs), p=[p for _, p in outs])
            return self._walk(g.next_state(state, outs[i][0]), trav)
        pl = g.current_player(state)
        acts = g.legal_actions(state)
        n = len(acts)
        key = g.infoset_key(state, pl)
        if key not in self.regret:
            self.regret[key] = np.zeros(n)
            self.strat_sum[key] = np.zeros(n)
            self.actions[key] = list(acts)
        sigma = self._strategy(key, n)
        if pl == trav:
            util = np.array([self._walk(g.next_state(state, a), trav) for a in acts])
            node = float(sigma @ util)
            self.regret[key] += util - node
            return node
        # opponent node: sample one action; average strategy accumulated here
        self.strat_sum[key] += sigma
        i = self.rng.choice(n, p=sigma)
        return self._walk(g.next_state(state, acts[i]), trav)

    def train(self, iterations):
        for _ in range(iterations):
            for trav in (0, 1):
                self._walk(self.game.initial_state(), trav)

    def average_strategy(self):
        out = {}
        for key, s in self.strat_sum.items():
            t = s.sum()
            p = s / t if t > 0 else np.full(len(s), 1.0 / len(s))
            out[key] = dict(zip(self.actions[key], p))
        return out
