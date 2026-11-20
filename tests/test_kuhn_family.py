from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from scripts.run_kuhn_cfr import family_violations


def test_average_strategy_in_equilibrium_family():
    c = CFR(KuhnPoker())
    c.train(5000)
    assert family_violations(c.average_strategy(), 0.05) == []
