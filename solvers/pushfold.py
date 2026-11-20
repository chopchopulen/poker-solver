"""Vectorized CFR+ for HU push/fold over hand classes.

SB (blinds 0.5/1) shoves or folds; BB calls or folds. SB payoff in BB:
fold -0.5; shove/fold +1; shove/call S*(2*eq-1). eq[i][j] = SB class i equity vs BB class j,
w[i][j] = # non-conflicting combo pairs (joint card-removal weight).
"""
import numpy as np


def _values(eq, w, S):
    """Return normalized joint weights m and A (SB payoff if shove/call)."""
    return w / w.sum(), S * (2.0 * eq - 1.0)


def sb_values(eq, w, S, call):
    """Per SB class: (shove value, fold value), weighted by prob of that class."""
    m, A = _values(eq, w, S)
    shove = (m * ((1.0 - call)[None, :] + call[None, :] * A)).sum(axis=1)
    fold = -0.5 * m.sum(axis=1)
    return shove, fold


def bb_values(eq, w, S, shove):
    """Per BB class: (call value, fold value) from BB's view (zero-sum, negated SB payoff)."""
    m, A = _values(eq, w, S)
    call = -(m * shove[:, None] * A).sum(axis=0)
    fold = -(m * shove[:, None]).sum(axis=0)
    return call, fold


def ev_sb(eq, w, S, shove, call):
    sv, fv = sb_values(eq, w, S, call)
    return float((shove * sv + (1 - shove) * fv).sum())


def exploitability(eq, w, S, shove, call):
    """(BR_SB(call) + BR_BB(shove)) / 2 in BB per hand; >= 0, 0 iff Nash."""
    sv, fv = sb_values(eq, w, S, call)
    br_sb = np.maximum(sv, fv).sum()
    cv, bfv = bb_values(eq, w, S, shove)
    m = w / w.sum()
    # BB gets +0.5 whenever SB folds; BB acts only after a shove
    fold_branch = 0.5 * ((1 - shove) * m.sum(axis=1)).sum()
    br_bb = fold_branch + np.maximum(cv, bfv).sum()
    return float((br_sb + br_bb) / 2)


def solve(eq, w, S, iters=2000, record_every=None):
    """CFR+ (regret clipping, linear averaging, alternating). Returns (avg_shove, avg_call, history)."""
    n = eq.shape[0]
    rs = np.zeros((n, 2))  # SB regrets [shove, fold]
    rb = np.zeros((n, 2))  # BB regrets [call, fold]
    s = np.full(n, 0.5)
    c = np.full(n, 0.5)
    ss = np.zeros(n)
    sc = np.zeros(n)
    tot = 0.0
    hist = []
    for t in range(1, iters + 1):
        sv, fv = sb_values(eq, w, S, c)
        d = sv - fv
        rs[:, 0] = np.maximum(rs[:, 0] + (1 - s) * d, 0)
        rs[:, 1] = np.maximum(rs[:, 1] - s * d, 0)
        z = rs.sum(axis=1)
        s = np.where(z > 0, rs[:, 0] / np.where(z > 0, z, 1), 0.5)
        cv, bf = bb_values(eq, w, S, s)
        d = cv - bf
        rb[:, 0] = np.maximum(rb[:, 0] + (1 - c) * d, 0)
        rb[:, 1] = np.maximum(rb[:, 1] - c * d, 0)
        z = rb.sum(axis=1)
        c = np.where(z > 0, rb[:, 0] / np.where(z > 0, z, 1), 0.5)
        ss += t * s
        sc += t * c
        tot += t
        if record_every and t % record_every == 0:
            hist.append((t, exploitability(eq, w, S, ss / tot, sc / tot)))
    return ss / tot, sc / tot, hist
