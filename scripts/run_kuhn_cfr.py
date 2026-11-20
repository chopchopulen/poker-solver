"""Run vanilla CFR on Kuhn, write analysis/kuhn_cfr.csv, print one summary line."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from eval.game_value import game_value


def family_violations(avg, tol):
    """Return list of equilibrium-family violations (empty = fits). b = bet/call prob.
    Keys: card + history; card 0=J,1=Q,2=K."""
    b = {k: float(v["b"]) for k, v in avg.items()}
    a = b["0"]  # alpha: P1 bets J
    checks = {
        "alpha in [0,1/3]": -tol <= a <= 1 / 3 + tol,
        "P1 K bet = 3a": abs(b["2"] - 3 * a) <= tol,
        "P1 Q check": b["1"] <= tol,
        "P1 Q call after pb = a+1/3": abs(b["1pb"] - (a + 1 / 3)) <= tol,
        "P1 J fold after pb": b["0pb"] <= tol,
        "P1 K call after pb": b["2pb"] >= 1 - tol,
        "P2 K bet after p": b["2p"] >= 1 - tol,
        "P2 K call after b": b["2b"] >= 1 - tol,
        "P2 J bluff 1/3 after p": abs(b["0p"] - 1 / 3) <= tol,
        "P2 Q check after p": b["1p"] <= tol,
        "P2 Q call 1/3 after b": abs(b["1b"] - 1 / 3) <= tol,
        "P2 J fold after b": b["0b"] <= tol,
    }
    return [k for k, ok in checks.items() if not ok]


def main(iters=100_000, out="analysis/kuhn_cfr.csv"):
    g = KuhnPoker()
    c = CFR(g)
    c.train(iters)
    avg = c.average_strategy()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["infoset", "p_pass", "p_bet"])
        for k in sorted(avg):
            w.writerow([k, "%.6f" % avg[k]["p"], "%.6f" % avg[k]["b"]])
    v = game_value(g, [avg, avg], 0)
    bad = family_violations(avg, 0.02)
    print("iters=%d P1 value=%.6f target=%.6f err=%.2e alpha=%.4f family_ok=%s"
          % (iters, v, -1 / 18, abs(v + 1 / 18), avg["0"]["b"], not bad))
    return v


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100_000)
