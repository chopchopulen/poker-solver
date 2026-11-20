import pytest

from games.kuhn import KuhnPoker

g = KuhnPoker()


def run(cards, hist):
    s = (cards, "")
    for a in hist:
        s = g.next_state(s, a)
    return s


def test_six_equal_deals():
    outs = g.chance_outcomes(g.initial_state())
    assert len(outs) == 6 and len(set(a for a, _ in outs)) == 6
    assert all(p == pytest.approx(1 / 6) for _, p in outs)
    assert sum(p for _, p in outs) == pytest.approx(1)


@pytest.mark.parametrize("hist,hi_wins_p0,expected", [
    ("pp", True, 1), ("pp", False, -1),
    ("bb", True, 2), ("bb", False, -2),
    ("pbb", True, 2), ("pbb", False, -2),
])
def test_showdown_payoffs(hist, hi_wins_p0, expected):
    cards = (2, 0) if hi_wins_p0 else (0, 2)
    s = run(cards, hist)
    assert g.is_terminal(s)
    assert g.utility(s, 0) == expected and g.utility(s, 1) == -expected


@pytest.mark.parametrize("cards", [(0, 2), (2, 0)])
def test_fold_payoffs_ignore_cards(cards):
    s = run(cards, "bp")
    assert (g.utility(s, 0), g.utility(s, 1)) == (1, -1)
    s = run(cards, "pbp")
    assert (g.utility(s, 0), g.utility(s, 1)) == (-1, 1)


def test_flow_and_players():
    s = g.initial_state()
    assert g.is_chance(s) and not g.is_terminal(s)
    s = g.next_state(s, (1, 2))
    assert not g.is_chance(s) and g.current_player(s) == 0
    s = g.next_state(s, "p")
    assert g.current_player(s) == 1
    s = g.next_state(s, "b")
    assert g.current_player(s) == 0 and not g.is_terminal(s)
    assert g.legal_actions(s) == ["p", "b"]


def test_terminals_only_after_correct_histories():
    for h in ["p", "b", "pb"]:
        assert not g.is_terminal(((0, 1), h))
    for h in ["pp", "bp", "bb", "pbp", "pbb"]:
        assert g.is_terminal(((0, 1), h))


def test_infoset_key_hides_opponent_card():
    a, b = run((0, 1), "pb"), run((0, 2), "pb")
    assert g.infoset_key(a, 0) == g.infoset_key(b, 0)
    c, d = run((0, 1), "p"), run((2, 1), "p")
    assert g.infoset_key(c, 1) == g.infoset_key(d, 1)
    assert g.infoset_key(a, 0) != g.infoset_key(run((1, 2), "pb"), 0)
    assert g.infoset_key(run((0, 1), "p"), 1) != g.infoset_key(run((0, 1), "b"), 1)
