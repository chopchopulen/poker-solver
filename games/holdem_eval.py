"""Vectorized numpy 7-card hand evaluator (higher score = better hand).

Cards are ints 0..51: card = rank*4 + suit, rank 0..12 = "23456789TJQKA",
suit 0..3 = "cdhs". Validated against treys in tests/test_pushfold_equity.py.
Used because treys is far too slow for ~1e8 evaluations (eval7 failed to build).
"""

import numpy as np

from games.holdem_classes import RANKS, SUITS

_R = np.arange(13)
_S = np.arange(4)
_BASE = 14 ** 5
_NREL = np.array([5, 4, 3, 3, 0, 0, 2, 2])  # relevant (count,rank) groups per category


def card_int(card: str) -> int:
    return RANKS.index(card[0]) * 4 + SUITS.index(card[1])


def _straight_high(P):
    """Highest straight top-rank (0-based, wheel = 3) in presence array P (N,13), else -1."""
    out = np.full(P.shape[0], -1)
    wheel = P[:, [12, 0, 1, 2, 3]].all(1)
    out[wheel] = 3
    for h in range(4, 13):
        out = np.where(P[:, h - 4:h + 1].all(1), h, out)
    return out


def score7(cards):
    """cards: int array (N,7). Returns int64 scores (N,); equal score = tie."""
    cards = np.asarray(cards)
    r = cards >> 2
    s = cards & 3
    oh = r[:, :, None] == _R  # (N,7,13)
    rc = oh.sum(1)  # (N,13)
    sc = (s[:, :, None] == _S).sum(1)
    fs = sc.argmax(1)
    hasf = sc.max(1) >= 5
    Pf = (oh & (s == fs[:, None])[:, :, None]).any(1) & hasf[:, None]

    # category from raw counts
    n4 = (rc == 4).any(1)
    n3 = (rc == 3).sum(1)
    n2 = (rc == 2).sum(1)
    cat = np.zeros(len(cards), dtype=np.int64)
    cat = np.where(n2 == 1, 1, cat)
    cat = np.where(n2 >= 2, 2, cat)
    cat = np.where((n3 == 1) & (n2 == 0), 3, cat)
    cat = np.where((n3 >= 1) & ((n2 >= 1) | (n3 >= 2)), 6, cat)
    cat = np.where(n4, 7, cat)

    # demote groups that must act as kickers
    rcm = rc.copy()
    q = np.where(n4)[0]
    rcm[q] = np.where(rc[q] == 4, 4, np.minimum(rc[q], 1))
    t = np.where(n2 == 3)[0]  # three pairs: lowest pair becomes a kicker
    low = (rc[t] == 2).argmax(1)
    rcm[t, low] = 1

    key = np.where(rcm > 0, rcm * 16 + _R, -1)
    top = -np.sort(-key, axis=1)[:, :5]
    vals = np.where(top >= 0, (top & 15) + 1, 0)
    vals = np.where(np.arange(5) < _NREL[cat][:, None], vals, 0)
    w = 14 ** np.arange(4, -1, -1)
    score = cat * _BASE + (vals * w).sum(1)

    # flush
    fk = -np.sort(-np.where(Pf, _R, -1), axis=1)[:, :5]
    fscore = 5 * _BASE + ((fk + 1) * w).sum(1)
    score = np.where(hasf, np.maximum(score, fscore), score)
    # straight / straight flush
    st = _straight_high(rc > 0)
    score = np.where(st >= 0, np.maximum(score, 4 * _BASE + (st + 1) * 14 ** 4), score)
    sf = _straight_high(Pf)
    score = np.where(sf >= 0, np.maximum(score, 8 * _BASE + (sf + 1) * 14 ** 4), score)
    return score
