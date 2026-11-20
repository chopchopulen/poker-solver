"""Adaptive agent: online opponent model + best response, blended with equilibrium.

Model (uses only what the agent sees: public betting history + board):
  counts[public][a] = times the opponent took action a in public situation `public`
  (= infoset key minus the acting player's own card, since the opp card is hidden).
  Opp strategy at infoset k=(card|public): Dirichlet posterior mean
      (alpha0 * eq[k][a] + counts[public][a]) / (alpha0 + n_public)
  Prior is centered on equilibrium; with no data the model IS equilibrium.
  Counts are pooled over opponent cards (hidden), so card-dependent opponents are
  approximated by their marginal action frequencies.
Play: at each infoset, mix (1-w)*equilibrium + w*BR-to-model, w = min(cap, n/(n+K)),
  n = number of observed opponent decisions.
"""
import numpy as np

from agents.base import Agent
from eval.best_response import best_response


class AdaptiveAgent(Agent):
    def __init__(self, game, eq_strategy, seed=0, alpha0=5.0, k=200.0, cap=1.0, refresh=50):
        self.game, self.eq = game, eq_strategy
        self.seed, self.alpha0, self.k, self.cap, self.refresh = seed, alpha0, k, cap, refresh
        self.reset()

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self.counts = {}      # public key -> {action: count}
        self.n = 0            # observed opponent decisions
        self._seen = 0        # actions of current hand already processed
        self._br = {}         # seat -> BR dict (stale until refresh)
        self._hands = 0
        self._br_hands = {}   # seat -> hands count at last BR computation

    def weight(self):
        return min(self.cap, self.n / (self.n + self.k))

    def model_strategy(self):
        out = {}
        for key, dist in self.eq.items():
            pub = key.split("|", 1)[1]
            c = self.counts.get(pub, {})
            tot = self.alpha0 + sum(c.values())
            out[key] = {a: (self.alpha0 * p + c.get(a, 0)) / tot for a, p in dist.items()}
        return out

    def _observe(self, hist, seat):
        """Record opponent actions in hist[self._seen:] (all from public history)."""
        rnd_len, board_seen = 0, False
        for idx, ch in enumerate(hist):
            if ch == "/":
                rnd_len, board_seen = 0, True
                continue
            player = rnd_len % 2
            if idx >= self._seen and player != seat:
                pub = f"{'' if not board_seen else self._board}|{hist[:idx]}"
                c = self.counts.setdefault(pub, {})
                c[ch] = c.get(ch, 0) + 1
                self.n += 1
            rnd_len += 1
        self._seen = len(hist)

    def act(self, game, state, infoset):
        seat = game.current_player(state)
        self._board = infoset.split("|")[1]
        self._observe(state[2], seat)
        legal = list(game.legal_actions(state))
        p = self.policy(seat, infoset, legal)
        return legal[self.rng.choice(len(legal), p=p)]

    def policy(self, seat, infoset, legal):
        """Action probabilities (no side effects) from current model."""
        w = self.weight()
        dist = self.eq.get(infoset)
        base = (np.array([dist.get(a, 0.0) for a in legal]) if dist is not None
                else np.ones(len(legal)))
        base = base / base.sum()
        if w > 0:
            br = self._best_response(seat)
            if infoset in br and br[infoset] in legal:
                pure = np.array([float(a == br[infoset]) for a in legal])
                base = (1 - w) * base + w * pure
        return base / base.sum()

    def _best_response(self, seat):
        if seat not in self._br or self._hands - self._br_hands[seat] >= self.refresh:
            strategies = [None, None]
            strategies[1 - seat] = self.model_strategy()
            self._br[seat] = best_response(self.game, strategies, seat)[1]
            self._br_hands[seat] = self._hands
        return self._br[seat]

    def observe_end(self, game, hist, seat):
        self._board = self._board if hasattr(self, "_board") else ""
        self._observe(hist, seat)
        self._seen = 0
        self._hands += 1
