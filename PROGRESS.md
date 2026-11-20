# Progress log
- P1.1 scaffold done: package inits, scripts/, requirements.txt, pytest.ini, tests/test_smoke.py; pytest -q 7 passed.
- P1.2 games/base.py abstract Game + tests/test_base.py; pytest -q 18 passed.
- P1.3 games/kuhn.py + tests/test_kuhn.py; payoffs hand-checked; pytest -q 30 passed.
- P1.4 solvers/cfr.py vanilla CFR + eval/game_value.py + tests/test_cfr.py; 2000 iters within 0.005 of -1/18; pytest -q 31 passed.
- P1.5 scripts/run_kuhn_cfr.py + analysis/kuhn_cfr.csv + tests/test_kuhn_family.py; 100k iters: value -0.055554 (err 2e-6 vs -1/18), alpha=0.22, family fits; pytest -q 32 passed. Repro: python scripts/run_kuhn_cfr.py
- P1.6 LEARNING.md Phase 1 entry + README Kuhn/CFR section and run command; pytest -q passes.
- P1.7 VERIFY: kuhn payoffs + cfr math reviewed; fixed CFR to freeze sigma per iteration (was changing mid-pass across deals); 100k iters: value -0.055555 (err 8.5e-7 vs -1/18), alpha=0.2053, family_ok=True; LEARNING math checked; pytest -q 32 passed. **Phase 1 DONE.** Repro: python scripts/run_kuhn_cfr.py
