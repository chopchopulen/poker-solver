import numpy as np
import pytest
from treys import Card, Evaluator

from games.holdem_classes import RANKS, SUITS
from games.holdem_eval import score7


def _tr(c):
    return Card.new(RANKS[c >> 2] + SUITS[c & 3])


def test_score7_matches_treys_ordering():
    ev = Evaluator()
    rng = np.random.default_rng(0)
    h = np.array([rng.choice(52, 7, replace=False) for _ in range(3000)])
    sc = score7(h)
    t = np.array([ev.evaluate([_tr(c) for c in x[5:]], [_tr(c) for c in x[:5]]) for x in h])
    o = np.argsort(t, kind="stable")
    s2, t2 = sc[o], t[o]
    assert (np.diff(s2) > 0).sum() == 0  # treys lower=better -> our score non-increasing
    assert ((np.diff(t2) == 0) & (np.diff(s2) != 0)).sum() == 0
    assert ((np.diff(t2) > 0) & (np.diff(s2) == 0)).sum() == 0


NPZ = "analysis/pushfold_equity.npz"


@pytest.fixture(scope="module")
def tab():
    import os
    if not os.path.exists(NPZ):
        pytest.skip("run scripts/pushfold_equity.py first")
    return np.load(NPZ)


def test_eq_antisymmetric_within_se(tab):
    eq, se = tab["eq"], tab["se"]
    off = ~np.eye(169, dtype=bool)
    assert np.all(np.abs(eq + eq.T - 1)[off] <= 2 * se[off] + 1e-9)
    assert se.max() < 0.002


def test_w_symmetric_and_known(tab):
    w = tab["w"]
    assert np.array_equal(w, w.T)
    assert w[0, 0] == 6  # AA vs AA: 6 combos, pairs of disjoint combos = 6
    assert w.sum() == 1326 * 1326 - _conflicts()


def _conflicts():
    from games.holdem_classes import HAND_CLASSES, class_combos
    cs = [set(c) for lab in HAND_CLASSES for c in class_combos(lab)]
    return sum(1 for a in cs for b in cs if a & b)
