from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from solvers.cfr_plus import CFRPlus
from eval.game_value import game_value
from eval.exploitability import exploitability


def test_cfr_plus_kuhn_value():
    g = KuhnPoker()
    c = CFRPlus(g)
    c.train(1000)
    avg = c.average_strategy()
    assert abs(game_value(g, [avg, avg], 0) - (-1 / 18)) < 0.005


def test_cfr_plus_regrets_nonneg():
    c = CFRPlus(KuhnPoker())
    c.train(50)
    assert all((r >= 0).all() for r in c.regret.values())


def test_cfr_plus_beats_vanilla():
    g = KuhnPoker()
    a, b = CFR(g), CFRPlus(g)
    a.train(1000)
    b.train(1000)
    sa, sb = a.average_strategy(), b.average_strategy()
    assert exploitability(g, [sb, sb]) < exploitability(g, [sa, sa])
