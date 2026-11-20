from games.leduc import LeducPoker
from solvers.cfr import CFR
from solvers.cfr_plus import CFRPlus
from eval.exploitability import exploitability
from tests.test_best_response import uniform_profile


def _expl(cls, iters):
    g = LeducPoker()
    s = cls(g)
    s.train(iters)
    a = s.average_strategy()
    return exploitability(g, [a, a])


def test_leduc_cfr_decreases():
    g = LeducPoker()
    base = exploitability(g, uniform_profile(g))
    e5, e20 = _expl(CFR, 5), _expl(CFR, 20)
    assert e20 < e5 < base


def test_leduc_cfr_plus_decreases():
    e5, e20 = _expl(CFRPlus, 5), _expl(CFRPlus, 20)
    assert 0 <= e20 < e5
