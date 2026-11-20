"""Build the results table (README.md + analysis/writeup.md) from analysis/*.csv; insert between markers.

Every row carries its reproduce command. Run: python scripts/make_results_table.py
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

from games.kuhn import KuhnPoker
from eval.game_value import game_value

START, END = "<!-- RESULTS_TABLE_START -->", "<!-- RESULTS_TABLE_END -->"
LEDUC_T = 140.0


def rd(name):
    with open(os.path.join(ROOT, "analysis", name), newline="") as f:
        return list(csv.DictReader(f))


def kuhn_value():
    avg = {r["infoset"]: {"p": float(r["p_pass"]), "b": float(r["p_bet"])}
           for r in rd("kuhn_cfr.csv")}
    return game_value(KuhnPoker(), [avg, avg], 0)


def kuhn_rows():
    rows = rd("kuhn_convergence.csv")
    out = {}
    for s in ("cfr", "cfr_plus"):
        r = [x for x in rows if x["solver"] == s]
        T = np.array([float(x["iter"]) for x in r])
        e = np.array([float(x["exploitability"]) for x in r])
        m = T >= 10_000
        slope = np.polyfit(np.log(T[m]), np.log(e[m]), 1)[0]
        out[s] = (e[-1], int(T[-1]), slope)
    return out


def leduc_at(t):
    rows = rd("leduc_benchmark.csv")
    res = {}
    for s in ("cfr", "cfr_plus", "mccfr"):
        r = [x for x in rows if x["solver"] == s and float(x["seconds"]) <= t]
        res[s] = float(r[-1]["mbb_per_hand"])
    return res


def pm(r):
    return "%+.0f±%.0f" % (float(r["mbb_per_hand"]), float(r["ci95_mbb"]))


def build():
    v = kuhn_value()
    k = kuhn_rows()
    sp = rd("kuhn_speedup.csv")[0]
    le = leduc_at(LEDUC_T)
    bots = ["always_call", "always_raise", "tight", "random"]
    short = {"always_call": "call", "always_raise": "raise", "tight": "tight", "random": "random"}
    bm = rd("bot_matches.csv")
    am = rd("adaptive_matches.csv")

    def get(rows, agent, bot):
        return next(r for r in rows if r["agent"] == agent and r["bot"] == bot)

    ex = ", ".join("%s %s" % (short[b], pm(get(bm, "exploiter", b))) for b in bots)
    eq = ", ".join(pm(get(bm, "equilibrium", b)) for b in bots)
    ad = ", ".join("%s %s / %s" % (short[b], pm(get(am, "adaptive_cap1.0", b)),
                                   pm(get(am, "adaptive_cap0.2", b))) for b in bots)
    ade = "%s / %s" % (pm(get(am, "adaptive_cap1.0", "equilibrium")),
                       pm(get(am, "adaptive_cap0.2", "equilibrium")))
    nb = bm[0]["n_hands"]
    na = am[0]["n_hands"]
    L = [
        "| Metric | Value | Command |",
        "|--------|-------|---------|",
        "| Kuhn game value (vanilla CFR, 100k iters) | %.6f (target -1/18 = %.6f) | `python scripts/run_kuhn_cfr.py` |" % (v, -1 / 18),
        "| Kuhn exploitability after %d iters (vanilla CFR) | %.2e (log-log slope %.3f, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr && python analysis/plot_convergence.py` |" % (k["cfr"][1], k["cfr"][0], k["cfr"][2]),
        "| Kuhn exploitability after %d iters (CFR+) | %.2e (log-log slope %.3f, T>=10k) | `python scripts/kuhn_convergence.py --solver cfr_plus && python analysis/plot_convergence.py` |" % (k["cfr_plus"][1], k["cfr_plus"][0], k["cfr_plus"][2]),
        "| CFR+ speedup vs vanilla (iters to expl < %g) | %.0fx (%s vs %s iters) | `python scripts/kuhn_convergence.py --solver cfr && python scripts/kuhn_convergence.py --solver cfr_plus` |" % (float(sp["target_exploitability"]), float(sp["speedup"]), sp["cfr_iters"], sp["cfr_plus_iters"]),
        "| Leduc exploitability (mbb/hand), last checkpoint within %g s: CFR / CFR+ / MCCFR | %.2f / %.4f / %.2f | `python scripts/leduc_benchmark.py && python analysis/plot_leduc.py` |" % (LEDUC_T, le["cfr"], le["cfr_plus"], le["mccfr"]),
        "| Exploiter (exact BR) vs bots, mbb/hand ±95%% CI, %dk hands each | %s (equilibrium: %s) | `python scripts/bot_matches.py --pairs 150000 --seed 0` |" % (int(nb) // 1000, ex, eq),
        "| Adaptive agent vs bots, mbb/hand ±95%% CI, %dk hands each (cap 1.0 / cap 0.2) | %s; vs equilibrium %s | `python scripts/adaptive_matches.py --pairs 20000 --seed 0` |" % (int(na) // 1000, ad, ade),
    ]
    L += mm_rows() + pushfold_rows()
    return "\n".join(L)


def mm_rows():
    ex = float(rd("mm_game_convergence.csv")[-1]["exploitability"])
    it = rd("mm_game_convergence.csv")[-1]["iter"]
    q = rd("mm_game_quotes.csv")
    dev = max(q, key=lambda r: abs(float(r["avg_mid"]) - float(r["E_V_given_mm_card"])))
    d = abs(float(dev["avg_mid"]) - float(dev["E_V_given_mm_card"]))
    info = [r for r in rd("mm_game_info.csv") if float(r["noise"]) == 0.25]
    inf = " / ".join("%.3f" % float(r["mm_ev_informed"]) for r in info)
    noise = float(info[0]["mm_ev_noise"])
    return [
        "| Market-making game: CFR+ exploitability after %s iters (deck 10, noise 0.25) | %.2e | `python scripts/mm_solve.py --iters %s` |" % (it, ex, it),
        "| Market-making: MM EV vs informed taker, taker_sees 0/1/2 (vs noise flow) | %s (%+.3f) | `python scripts/mm_info.py --iters 1000` |" % (inf, noise),
        "| Market-making: max abs(avg mid - E[V given MM card]) | %.2f (card %s); spread at grid max 4 | `python scripts/mm_quotes.py` |" % (d, dev["mm_card"]),
    ]


def pushfold_rows():
    s = rd("pushfold_summary.csv")
    by = {int(r["stack"]): r for r in s}
    mx = max(s, key=lambda r: float(r["exploitability_bb"]))
    se = float(np.load(os.path.join(ROOT, "analysis", "pushfold_equity.npz"))["se"].max())
    return [
        "| Push/fold (HU NL, stacks 1-20 BB): max exploitability | %.2e BB/hand (S=%s) | `python scripts/pushfold_solve.py` |" % (float(mx["exploitability_bb"]), mx["stack"]),
        "| Push/fold shove%% / call%% (combo-weighted), S=1 / 10 / 20 | %s / %s / %s ; %s / %s / %s | `python scripts/pushfold_solve.py` |" % tuple(
            "%.1f" % float(by[k][c]) for c in ("shove_pct", "call_pct") for k in (1, 10, 20)),
        "| Push/fold equity table: max Monte Carlo std err | %.4f | `python scripts/pushfold_equity.py --boards 120000 --validate` |" % se,
    ]


def write(p, table):
    text = open(p).read()
    if START not in text or END not in text:
        # first run: replace existing table (header row through last table row) with markers
        lines = text.split("\n")
        i = next(n for n, l in enumerate(lines) if l.startswith("| Metric |"))
        j = i
        while j + 1 < len(lines) and lines[j + 1].startswith("|"):
            j += 1
        lines[i:j + 1] = [START, END]
        text = "\n".join(lines)
    a, b = text.index(START) + len(START), text.index(END)
    text = text[:a] + "\n" + table + "\n" + text[b:]
    open(p, "w").write(text)


def main():
    t = build()
    for name in ("README.md", os.path.join("analysis", "writeup.md")):
        write(os.path.join(ROOT, name), t)
    print("results table updated in README.md and analysis/writeup.md (%d rows)" % (t.count("\n") - 1))


if __name__ == "__main__":
    main()
