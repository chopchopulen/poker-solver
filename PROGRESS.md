# Progress log
- P1.1 scaffold done: package inits, scripts/, requirements.txt, pytest.ini, tests/test_smoke.py; pytest -q 7 passed.
- P1.2 games/base.py abstract Game + tests/test_base.py; pytest -q 18 passed.
- P1.3 games/kuhn.py + tests/test_kuhn.py; payoffs hand-checked; pytest -q 30 passed.
- P1.4 solvers/cfr.py vanilla CFR + eval/game_value.py + tests/test_cfr.py; 2000 iters within 0.005 of -1/18; pytest -q 31 passed.
