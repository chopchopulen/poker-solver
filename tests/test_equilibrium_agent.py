import os

import pytest

from agents.equilibrium import EquilibriumAgent
from games.kuhn import KuhnPoker
from games.leduc import LeducPoker
from solvers.cfr_plus import CFRPlus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def decision_states(game):
    out, stack = [], [game.initial_state()]
    while stack:
        s = stack.pop()
        if game.is_terminal(s):
            continue
        if game.is_chance(s):
            stack += [game.next_state(s, a) for a, _ in game.chance_outcomes(s)]
        else:
            out.append(s)
            stack += [game.next_state(s, a) for a in game.legal_actions(s)]
    return out


@pytest.mark.parametrize("game", [KuhnPoker(), LeducPoker()])
def test_only_legal_actions(game):
    s = CFRPlus(game)
    s.train(20)
    ag = EquilibriumAgent(s.average_strategy(), seed=1)
    for st in decision_states(game):
        key = game.infoset_key(st, game.current_player(st))
        for _ in range(5):
            assert ag.act(game, st, key) in game.legal_actions(st)


def test_frequencies_match_stored_probs_and_seeded():
    g = KuhnPoker()
    s = CFRPlus(g)
    s.train(200)
    strat = s.average_strategy()
    ag = EquilibriumAgent(strat, seed=3)
    st = decision_states(g)[0]
    key = g.infoset_key(st, g.current_player(st))
    n = 4000
    acts = [ag.act(g, st, key) for _ in range(n)]
    for a, p in strat[key].items():
        assert abs(acts.count(a) / n - p) < 0.04
    ag.reset()
    assert [ag.act(g, st, key) for _ in range(50)] == acts[:50]


def test_saved_json_loads_and_normalized():
    path = os.path.join(ROOT, "analysis", "strategies", "kuhn.json")
    ag = EquilibriumAgent.from_json(path)
    for d in ag.strategy.values():
        assert abs(sum(d.values()) - 1) < 1e-6
    g = KuhnPoker()
    st = decision_states(g)[0]
    assert ag.act(g, st, g.infoset_key(st, g.current_player(st))) in g.legal_actions(st)
