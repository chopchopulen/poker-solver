from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from eval.game_value import game_value


def test_kuhn_value_converges():
    g = KuhnPoker()
    c = CFR(g)
    c.train(2000)
    avg = c.average_strategy()
    v = game_value(g, [avg, avg], 0)
    assert abs(v - (-1 / 18)) < 0.005
    assert abs(game_value(g, [avg, avg], 1) + v) < 1e-9
