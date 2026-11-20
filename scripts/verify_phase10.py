"""Phase 10 verification, independent of solvers/pushfold.py's vectorized formulas.

(1) card-removal weights: brute-force count of disjoint combo pairs from card strings vs npz w
(2) exploitability for 2 stacks recomputed at the COMBO level (1326 x 1326) straight from the
    game definition: blinds 0.5/1, SB fold -0.5, shove/fold +1, shove/call S*(2*eq-1)
(3) equity spot-checks vs exact full-board enumeration for 2 class pairs not in the P10.2 set
(4) evaluator spot-check: score7 ordering vs treys on random 7-card hand pairs
(5) combo-weighted shove%/call% non-increasing in stack (ranges widen as stack shrinks)
Usage: python scripts/verify_phase10.py [--stacks 5 15]. Prints one summary line per check."""
import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from games.holdem_classes import CLASS_INDEX, HAND_CLASSES, class_combos  # noqa: E402
from games.holdem_eval import card_int, score7  # noqa: E402

NPZ = "analysis/pushfold_equity.npz"
RANGES = "analysis/pushfold_ranges.csv"
SUMMARY = "analysis/pushfold_summary.csv"


def check_weights(w):
    combos = {h: [frozenset(c) for c in class_combos(h)] for h in HAND_CLASSES}
    pairs = [("AA", "AA"), ("AA", "KK"), ("AKs", "AKo"), ("AKs", "AA"), ("72o", "72o"),
             ("T9s", "98s"), ("QJo", "JTo"), ("55", "A5s")]
    bad = 0
    for a, b in pairs:
        n = sum(1 for x in combos[a] for y in combos[b] if not (x & y))
        bad += n != w[CLASS_INDEX[a], CLASS_INDEX[b]]
    total_ok = w.sum() == 1326 * 1225
    print(f"[weights] {len(pairs) - bad}/{len(pairs)} class pairs match brute force; "
          f"sum w = {w.sum():.0f} (1326*1225 = {1326 * 1225}) {'OK' if total_ok else 'FAIL'}")
    return bad == 0 and total_ok


def load_strategy(S):
    s, c = np.zeros(169), np.zeros(169)
    with open(RANGES) as f:
        for r in csv.DictReader(f):
            if int(r["stack"]) == S:
                i = CLASS_INDEX[r["hand"]]
                s[i], c[i] = float(r["shove"]), float(r["call"])
    return s, c


def combo_exploitability(eq, S, s, c):
    """Combo-level best responses. Each disjoint (sb_combo, bb_combo) pair equally likely."""
    cards, cls = [], []
    for h in HAND_CLASSES:
        for a, b in class_combos(h):
            cards.append((card_int(a), card_int(b)))
            cls.append(CLASS_INDEX[h])
    cards, cls = np.array(cards), np.array(cls)
    n = len(cls)
    share = (cards[:, None, 0] == cards[None, :, 0]) | (cards[:, None, 0] == cards[None, :, 1]) \
        | (cards[:, None, 1] == cards[None, :, 0]) | (cards[:, None, 1] == cards[None, :, 1])
    P = (~share).astype(float)
    P /= P.sum()  # joint deal probability over (sb combo, bb combo)
    E = eq[cls][:, cls]  # SB equity per combo pair
    showdown = S * (2 * E - 1)  # SB net when shove is called
    sb_s, bb_c = s[cls], c[cls]

    def u_sb(shv, cal):  # SB expected payoff for behavioral strategies over combos
        shv, cal = shv[:, None], cal[None, :]
        pay = (1 - shv) * -0.5 + shv * ((1 - cal) * 1.0 + cal * showdown)
        return float((P * pay).sum())

    v = u_sb(sb_s, bb_c)
    # SB best response vs fixed BB calls: per SB combo pick the better pure action
    shove_val = (P * ((1 - bb_c)[None, :] + bb_c[None, :] * showdown)).sum(1)
    fold_val = -0.5 * P.sum(1)
    br_sb = float(np.maximum(shove_val, fold_val).sum())
    # BB best response vs fixed SB shoves: BB minimizes SB payoff per BB combo (facing a shove)
    call_cost = (P * sb_s[:, None] * showdown).sum(0)
    fold_cost = (P * sb_s[:, None] * 1.0).sum(0)
    sb_fold_part = (P * (1 - sb_s)[:, None] * -0.5).sum()
    min_sb = float(sb_fold_part + np.minimum(call_cost, fold_cost).sum())
    return v, br_sb, min_sb, (br_sb - min_sb) / 2


def check_evaluator(n=20000, seed=7):
    from treys import Card, Evaluator
    ev = Evaluator()
    rng = np.random.default_rng(seed)
    R, St = "23456789TJQKA", "cdhs"
    bad = 0
    for _ in range(n // 100):
        d = np.array([rng.permutation(52)[:9] for _ in range(100)])
        a = np.concatenate([d[:, :2], d[:, 4:]], 1)
        b = np.concatenate([d[:, 2:4], d[:, 4:]], 1)
        sa, sb = score7(a), score7(b)
        for k in range(100):
            tc = lambda x: Card.new(R[x >> 2] + St[x & 3])
            board = [tc(x) for x in d[k, 4:]]
            ta = ev.evaluate([tc(x) for x in d[k, :2]], board)
            tb = ev.evaluate([tc(x) for x in d[k, 2:4]], board)  # treys: lower = better
            bad += np.sign(sa[k] - sb[k]) != np.sign(tb - ta)
    print(f"[evaluator] score7 vs treys: {n - bad}/{n} hand pairs same winner {'OK' if bad == 0 else 'FAIL'}")
    return bad == 0


def check_monotone():
    rows = list(csv.DictReader(open(SUMMARY)))
    sh = [float(r["shove_pct"]) for r in rows]
    ca = [float(r["call_pct"]) for r in rows]
    ok = all(x >= y for x, y in zip(sh, sh[1:])) and all(x >= y for x, y in zip(ca, ca[1:]))
    print(f"[ranges] shove% S=1..20 non-increasing and call% non-increasing: {'OK' if ok else 'FAIL'} "
          f"(shove {sh[0]:.1f}% -> {sh[-1]:.1f}%, call {ca[0]:.1f}% -> {ca[-1]:.1f}%)")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stacks", type=int, nargs="+", default=[5, 15])
    ap.add_argument("--skip-exact", action="store_true")
    a = ap.parse_args()
    d = np.load(NPZ)
    eq, w, se = d["eq"], d["w"], d["se"]
    ok = check_weights(w)
    ok &= check_evaluator()
    from solvers.pushfold import exploitability
    for S in a.stacks:
        s, c = load_strategy(S)
        v, br_sb, min_sb, ex = combo_exploitability(eq, S, s, c)
        ex_solver = exploitability(eq, w, S, s, c)
        good = abs(ex - ex_solver) < 1e-9 and ex < 1e-3 and br_sb >= v - 1e-12 and min_sb <= v + 1e-12
        ok &= good
        print(f"[expl S={S}] SB value {v:.6f} BB; combo-level expl {ex:.3e} vs solver {ex_solver:.3e} "
              f"{'OK' if good else 'FAIL'}")
    if not a.skip_exact:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from pushfold_equity import exact_equity
        for li, lj in [("22", "AKo"), ("KQs", "JTs")]:
            ex = exact_equity(li, lj)
            i, j = CLASS_INDEX[li], CLASS_INDEX[lj]
            err = abs(eq[i, j] - ex)
            good = err < 3 * se[i, j] + 1e-4
            ok &= good
            print(f"[equity {li}v{lj}] mc {eq[i, j]:.5f} exact {ex:.5f} err {err:.5f} "
                  f"se {se[i, j]:.5f} {'OK' if good else 'FAIL'}")
    ok &= check_monotone()
    print("PHASE 10 VERIFY:", "ALL PASS" if ok else "FAILURES")


if __name__ == "__main__":
    main()
