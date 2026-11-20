"""CFR+ : regret-matching+ (regrets floored at 0), alternating updates,
linearly weighted average strategy (weight t on iteration t)."""
import numpy as np
from solvers.cfr import CFR


class CFRPlus(CFR):
    def __init__(self, game):
        super().__init__(game)
        self.owner = {}   # key -> player
        self.t = 0
        self._upd = 0     # player being updated this pass

    def _walk(self, state, reach):
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
            self.owner[key] = pl
        if key not in self._sigma:
            self._sigma[key] = self._strategy(key, n)  # regrets already >= 0
        sigma = self._sigma[key]
        util = np.zeros(n)
        for i, a in enumerate(acts):
            r = list(reach)
            r[pl] *= sigma[i]
            util[i] = self._walk(g.next_state(state, a), r)
        node = float(sigma @ util)
        if pl == self._upd:  # only the updating player's infosets change
            sign = 1.0 if pl == 0 else -1.0
            cf = reach[1 - pl] * reach[2]
            self.regret[key] += cf * sign * (util - node)
            self.strat_sum[key] += self.t * reach[pl] * sigma
        return node

    def train(self, iterations):
        for _ in range(iterations):
            self.t += 1
            for p in (0, 1):
                self._upd = p
                self._sigma = {}
                self._walk(self.game.initial_state(), [1.0, 1.0, 1.0])
                for k, o in self.owner.items():  # floor after the pass (the "+")
                    if o == p:
                        np.maximum(self.regret[k], 0.0, out=self.regret[k])
