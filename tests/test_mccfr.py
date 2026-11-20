from games.kuhn import KuhnPoker
from games.leduc import LeducPoker
from solvers.mccfr import MCCFR
from eval.exploitability import exploitability
from eval.game_value import game_value


def test_mccfr_kuhn_value():
    g = KuhnPoker()
    s = MCCFR(g, seed=1)
    s.train(20000)
    a = s.average_strategy()
    assert abs(game_value(g, [a, a], 0) - (-1 / 18)) < 0.02


def test_mccfr_leduc_decreases():
    g = LeducPoker()

    def e(n):
        s = MCCFR(g, seed=0)
        s.train(n)
        a = s.average_strategy()
        return exploitability(g, [a, a])
    assert e(3000) < e(100)


def test_mccfr_seeded():
    g = KuhnPoker()
    a, b = MCCFR(g, seed=5), MCCFR(g, seed=5)
    a.train(200); b.train(200)
    assert a.average_strategy() == b.average_strategy()
