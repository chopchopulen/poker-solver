from games.kuhn import KuhnPoker
from solvers.cfr import CFR
from eval.game_value import game_value
from eval.best_response import best_response_value


def uniform_profile(game):
    strat = [{}, {}]

    def walk(s):
        if game.is_terminal(s):
            return
        if game.is_chance(s):
            for a, _ in game.chance_outcomes(s):
                walk(game.next_state(s, a))
            return
        pl = game.current_player(s)
        acts = game.legal_actions(s)
        strat[pl][game.infoset_key(s, pl)] = {a: 1 / len(acts) for a in acts}
        for a in acts:
            walk(game.next_state(s, a))
    walk(game.initial_state())
    return strat


def test_br_vs_equilibrium_equals_game_value():
    g = KuhnPoker()
    c = CFR(g)
    c.train(20000)
    avg = c.average_strategy()
    for p, v in ((0, -1 / 18), (1, 1 / 18)):
        assert abs(best_response_value(g, [avg, avg], p) - v) < 3e-3


def test_br_vs_uniform_at_least_uniform_value():
    g = KuhnPoker()
    u = uniform_profile(g)
    for p in (0, 1):
        assert best_response_value(g, u, p) >= game_value(g, u, p) - 1e-12


def test_br_vs_exact_equilibrium_is_tight():
    """Analytic Kuhn equilibrium (alpha=0.2): BR must equal game value to 1e-9."""
    a = 0.2

    def d(b):
        return {"p": 1 - b, "b": b}
    s0 = {"0": d(a), "1": d(0.0), "2": d(3 * a),
          "0pb": d(0.0), "1pb": d(a + 1 / 3), "2pb": d(1.0)}
    s1 = {"0p": d(1 / 3), "1p": d(0.0), "2p": d(1.0),
          "0b": d(0.0), "1b": d(1 / 3), "2b": d(1.0)}
    g = KuhnPoker()
    assert set(s0) == set(uniform_profile(g)[0]) and set(s1) == set(uniform_profile(g)[1])
    assert abs(best_response_value(g, [s0, s1], 0) + 1 / 18) < 1e-9
    assert abs(best_response_value(g, [s0, s1], 1) - 1 / 18) < 1e-9
