"""169x169 all-in preflop equity table (ties = half) with card removal.

eq[i][j] = P(class-i hand beats class-j hand) over uniform non-conflicting combo
pairs and uniform 5-card boards (ratio estimator, Monte Carlo over boards).
w[i][j]  = # non-conflicting (combo_i, combo_j) pairs (exact).
Std error from independent chunks of boards. --validate compares a few class
pairs to exact full-board enumeration (suit-isomorphism orbits).

Repro: python scripts/pushfold_equity.py --boards 30000 --validate
"""

import argparse
import itertools
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.holdem_classes import CLASS_INDEX, HAND_CLASSES, class_combos  # noqa: E402
from games.holdem_eval import card_int, score7  # noqa: E402

OUT = "analysis/pushfold_equity.npz"
VAL_CSV = "analysis/pushfold_equity_validation.csv"
CHUNK = 200


def build_tables():
    combos, cls = [], []
    for k, lab in enumerate(HAND_CLASSES):
        for a, b in class_combos(lab):
            combos.append((card_int(a), card_int(b)))
            cls.append(k)
    combos = np.array(combos)
    cls = np.array(cls)
    M = np.zeros((len(combos), 52), dtype=np.float32)
    M[np.arange(len(combos)), combos[:, 0]] = 1
    M[np.arange(len(combos)), combos[:, 1]] = 1
    notK = ((M @ M.T) == 0).astype(np.float32)  # True if no shared card (incl. self? no: self shares)
    C = np.zeros((len(combos), 169), dtype=np.float32)
    C[np.arange(len(combos)), cls] = 1
    return combos, M, notK, C


_T = None


def _init():
    global _T
    _T = build_tables()


def _chunk(args):
    k, seed, n = args
    combos, M, notK, C = _T
    rng = np.random.default_rng([seed, k])
    num = np.zeros((169, 169))
    den = np.zeros((169, 169))
    for _ in range(n):
        board = rng.permutation(52)[:5]
        idx = np.where(M[:, board].sum(1) == 0)[0]
        hands = np.concatenate([combos[idx], np.broadcast_to(board, (len(idx), 5))], axis=1)
        s = score7(hands)
        W = (s[:, None] > s[None, :]) + 0.5 * (s[:, None] == s[None, :])
        N = notK[np.ix_(idx, idx)]
        Ci = C[idx]
        num += (Ci.T @ (W.astype(np.float32) * N)) @ Ci
        den += (Ci.T @ N) @ Ci
    return num, den


def compute(boards, seed, workers):
    nch = max(1, boards // CHUNK)
    with Pool(workers, initializer=_init) as p:
        res = p.map(_chunk, [(k, seed, CHUNK) for k in range(nch)], chunksize=1)
    nums = np.array([r[0] for r in res])
    dens = np.array([r[1] for r in res])
    eq = nums.sum(0) / dens.sum(0)
    ch = nums / np.maximum(dens, 1e-12)
    se = ch.std(0, ddof=1) / np.sqrt(nch)
    return eq, se, nch * CHUNK


def exact_w():
    _, _, notK, C = build_tables()
    return C.T @ notK @ C


# ---- exact validation ----
def _orbits(i, j):
    """Orbits of (combo_i, combo_j) non-conflicting pairs under 24 suit permutations."""
    perms = list(itertools.permutations(range(4)))
    cnt = {}
    for a in class_combos(HAND_CLASSES[i]):
        for b in class_combos(HAND_CLASSES[j]):
            ca, cb = (card_int(x) for x in a), (card_int(x) for x in b)
            ca, cb = tuple(ca), tuple(cb)
            if set(ca) & set(cb):
                continue
            best = None
            for p in perms:
                f = lambda c: (c >> 2) * 4 + p[c & 3]
                key = (tuple(sorted(map(f, ca))), tuple(sorted(map(f, cb))))
                if best is None or key < best:
                    best = key
            cnt[best] = cnt.get(best, 0) + 1
    return cnt


def exact_equity(lab_i, lab_j):
    i, j = CLASS_INDEX[lab_i], CLASS_INDEX[lab_j]
    tot = wsum = 0.0
    for (a, b), size in _orbits(i, j).items():
        rest = np.array([c for c in range(52) if c not in a + b])
        wins = 0.0
        it = itertools.combinations(rest, 5)
        while True:
            blk = np.array(list(itertools.islice(it, 300000)))
            if len(blk) == 0:
                break
            ha = np.concatenate([np.broadcast_to(a, (len(blk), 2)), blk], axis=1)
            hb = np.concatenate([np.broadcast_to(b, (len(blk), 2)), blk], axis=1)
            sa, sb = score7(ha), score7(hb)
            wins += (sa > sb).sum() + 0.5 * (sa == sb).sum()
        tot += size * wins / math.comb(48, 5)
        wsum += size
    return tot / wsum


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    t0 = time.time()
    eq, se, samples = compute(a.boards, a.seed, a.workers)
    w = exact_w()
    np.savez(a.out, eq=eq, se=se, w=w, labels=np.array(HAND_CLASSES), samples=samples, seed=a.seed)
    print(f"boards={samples} max_se={se.max():.5f} mean_se={se.mean():.5f} "
          f"w[AA,AA]={w[0, 0]:.0f} time={time.time() - t0:.0f}s -> {a.out}")
    if a.validate:
        rows = ["pair,mc_eq,exact_eq,abs_err,mc_se"]
        for li, lj in [("AA", "KK"), ("AKs", "QQ"), ("AKo", "72o")]:
            ex = exact_equity(li, lj)
            i, j = CLASS_INDEX[li], CLASS_INDEX[lj]
            rows.append(f"{li}v{lj},{eq[i, j]:.5f},{ex:.5f},{abs(eq[i, j] - ex):.5f},{se[i, j]:.5f}")
            print(rows[-1])
        with open(VAL_CSV, "w") as f:
            f.write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
