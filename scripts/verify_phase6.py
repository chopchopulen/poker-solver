"""Phase 6 checks on analysis/adaptive_matches.csv (from scripts/adaptive_matches.py):
  1. adaptive (each cap) beats equilibrium vs every weak bot: adaptive CI lower bound > equilibrium CI upper bound
  2. safe vs equilibrium: adaptive CI lower bound > -50 mbb/hand
Leakage is checked by tests/test_adaptive.py::test_no_leakage_of_opponent_card.
Usage: python scripts/verify_phase6.py"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = {(r["agent"], r["bot"]): r for r in csv.DictReader(open(os.path.join(ROOT, "analysis", "adaptive_matches.csv")))}
bots = sorted({b for a, b in rows if a == "equilibrium"})
ok, msgs = True, []
for cap in ("adaptive_cap1.0", "adaptive_cap0.2"):
    for b in bots:
        lo, eq_hi = float(rows[(cap, b)]["lo_mbb"]), float(rows[("equilibrium", b)]["hi_mbb"])
        ok &= lo > eq_hi
        msgs.append(f"{cap} vs {b}: lo {lo:.0f} > eq hi {eq_hi:.0f}: {lo > eq_hi}")
    lo = float(rows[(cap, "equilibrium")]["lo_mbb"])
    ok &= lo > -50
    msgs.append(f"{cap} vs equilibrium: lo {lo:.1f} > -50: {lo > -50}")
print("\n".join(msgs) if not ok else "", end="")
print(f"Phase 6 checks {'PASS' if ok else 'FAIL'} ({len(msgs)} checks)")
