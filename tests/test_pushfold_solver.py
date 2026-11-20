import numpy as np
from solvers.pushfold import solve, exploitability, ev_sb

# 3 classes, monotone equities (class 0 strongest); eq[i][j]+eq[j][i]=1
EQ = np.array([[0.5, 0.7, 0.9], [0.3, 0.5, 0.7], [0.1, 0.3, 0.5]])
W = np.array([[1.0, 2, 2], [2, 1, 2], [2, 2, 1]])


def test_threshold_strategies():
    s, c, _ = solve(EQ, W, 2.0, iters=3000)
    assert np.all(np.diff(s) <= 1e-2)  # stronger hands shove at least as often
    assert np.all(np.diff(c) <= 1e-2)
    assert s[0] > 0.99 and c[0] > 0.99


def test_exploitability_decreases_and_small():
    _, _, h = solve(EQ, W, 2.0, iters=2000, record_every=100)
    assert h[-1][1] < h[0][1]
    assert h[-1][1] < 1e-3


def test_exploitability_nonneg_and_bad_strategy():
    z = np.zeros(3)
    assert exploitability(EQ, W, 2.0, z, z) > 0.05
    s, c, _ = solve(EQ, W, 2.0, iters=3000)
    assert exploitability(EQ, W, 2.0, s, c) >= -1e-12


def test_always_fold_sb_value():
    assert abs(ev_sb(EQ, W, 2.0, np.zeros(3), np.ones(3)) + 0.5) < 1e-12


def test_real_table_stack_1():
    d = np.load("analysis/pushfold_equity.npz")
    s, c, h = solve(d["eq"], d["w"], 1.0, iters=300, record_every=300)
    assert h[-1][1] < 0.05
