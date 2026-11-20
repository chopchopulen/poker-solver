"""Adaptive agent: online opponent model + best response, blended with equilibrium.

Model (uses only what the agent sees: its own card, the board, public betting history):
  counts[(own, public)][a] = times the opponent took action a at public node `public`
  while the agent held rank `own`. The opponent's card is never observed.
  Opp strategy for hidden card c at that node: sigma(c,a) ∝ eq_eps(c,a) * lam_a, with lam
  fitted so the predicted marginal sum_c w_c sigma(c,a) matches the Dirichlet posterior mean
  of the observed frequencies (prior = eq marginal, strength alpha0), where
  w_c ∝ P(opp=c, board | own) * opp reach of c under the model (card removal included).
  With no data the model IS equilibrium; vs an equilibrium opponent it stays near equilibrium.
Play: at each infoset, mix (1-w)*equilibrium + w*BR-to-model, w = min(cap, n/(n+K)),
  n = number of observed opponent decisions. BR for own card o is computed against the
  model fitted from the hands where the agent held o.
"""
import numpy as np

from agents.base import Agent
from eval.best_response import best_response

N_RANKS, PER_RANK = 3, 2  # Leduc deck: J,Q,K x 2


class AdaptiveAgent(Agent):
    def __init__(self, game, eq_strategy, seed=0, alpha0=5.0, k=200.0, cap=1.0, refresh=50):
        self.game, self.eq = game, eq_strategy
        self.seed, self.alpha0, self.k, self.cap, self.refresh = seed, alpha0, k, cap, refresh
        self.groups = {}  # public key -> opp ranks with an eq infoset there
        for key in eq_strategy:
            card, pub = key.split("|", 1)
            self.groups.setdefault(pub, []).append(card)
        self.order = sorted(self.groups, key=lambda p: len(p.rsplit("|", 1)[-1]))
        self.reset()

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self.counts = {}      # (own rank, public key) -> {action: count}
        self.n = 0            # observed opponent decisions
        self._seen = 0        # actions of current hand already processed
        self._br = {}         # seat -> BR dict (stale until refresh)
        self._hands = 0
        self._br_hands = {}   # seat -> hands count at last BR computation

    def weight(self):
        return min(self.cap, self.n / (self.n + self.k))

    def model_strategy(self, eps=0.01, iters=30):
        """Opponent model (one strategy: opp can't see the agent's card). Top-down in history length."""
        out = {}
        for pub in self.order:
            cards = self.groups[pub]
            per_own = {o: self.counts.get((o, pub), {}) for o in map(str, range(N_RANKS))}
            n_own = {o: sum(c.values()) for o, c in per_own.items()}
            n = sum(n_own.values())
            if n == 0:
                for c in cards:
                    out[f"{c}|{pub}"] = self.eq[f"{c}|{pub}"]
                continue
            reach = np.array([_reach(out, c, pub) for c in cards])
            w = np.zeros(len(cards))  # opp-card distribution over the observed deals at pub
            for o, m in n_own.items():
                if m:
                    wo = np.array([_prior(c, o, pub) for c in cards]) * reach
                    if wo.sum() > 0:
                        w += (m / n) * wo / wo.sum()
            w = w / w.sum() if w.sum() > 0 else np.full(len(cards), 1 / len(cards))
            acts = list(self.eq[f"{cards[0]}|{pub}"])
            base = np.array([[self.eq[f"{c}|{pub}"].get(a, 0.0) for a in acts] for c in cards])
            base = (1 - eps) * base + eps / len(acts)
            obs = np.array([sum(per_own[o].get(a, 0) for o in per_own) for a in acts])
            p_hat = (self.alpha0 * (w @ base) + obs) / (self.alpha0 + n)
            lam = np.ones(len(acts))
            for _ in range(iters):  # iterative proportional fitting of the marginal
                sig = base * lam
                sig /= sig.sum(axis=1, keepdims=True)
                lam *= p_hat / (w @ sig)
            sig = base * lam
            sig /= sig.sum(axis=1, keepdims=True)
            for i, c in enumerate(cards):
                out[f"{c}|{pub}"] = dict(zip(acts, sig[i]))
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
                c = self.counts.setdefault((self._card, pub), {})
                c[ch] = c.get(ch, 0) + 1
                self.n += 1
            rnd_len += 1
        self._seen = len(hist)

    def act(self, game, state, infoset):
        seat = game.current_player(state)
        self._card, self._board = infoset.split("|")[:2]  # own card + board: agent's view
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
        # agent acts in every Leduc hand, so _card/_board were set by act() this hand
        self._observe(hist, seat)
        self._seen = 0
        self._hands += 1


def _prior(card, own, pub):
    """Relative P(opp rank = card, board | own rank), from remaining deck counts."""
    left = {str(r): PER_RANK for r in range(N_RANKS)}
    left[own] -= 1
    p = left[card]
    board = pub.split("|")[0]
    if board:
        left[card] -= 1
        p *= max(left[board], 0)
    return float(p)


def _reach(out, card, pub):
    """Product of the actor's own earlier action probs along the public history."""
    board, hist = pub.split("|")
    actor = len(hist.split("/")[-1]) % 2
    r, rnd_len, seen = 1.0, 0, False
    for idx, ch in enumerate(hist):
        if ch == "/":
            rnd_len, seen = 0, True
            continue
        if rnd_len % 2 == actor:
            r *= out[f"{card}|{board if seen else ''}|{hist[:idx]}"][ch]
        rnd_len += 1
    return r
