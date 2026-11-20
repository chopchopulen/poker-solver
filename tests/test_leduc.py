import pytest

from games.leduc import LeducPoker

g = LeducPoker()


def run(cards, hist, board=None):
    s = g.next_state(g.initial_state(), cards)
    for a in hist:
        if a == "/":
            s = g.next_state(s, board)
        else:
            s = g.next_state(s, a)
    return s


def test_deal_count():
    outs = g.chance_outcomes(g.initial_state())
    assert len(outs) == 30 and len(set(a for a, _ in outs)) == 30
    assert sum(p for _, p in outs) == pytest.approx(1)


def test_board_chance():
    s = run((0, 3), "cc/")
    assert g.is_chance(s)
    outs = g.chance_outcomes(s)
    assert len(outs) == 4 and {a for a, _ in outs} == {1, 2, 4, 5}
    assert sum(p for _, p in outs) == pytest.approx(1)


def test_fold_payoffs():
    s = run((0, 2), "rf")  # P0 raises 2, P1 folds: P0 wins P1 ante
    assert g.is_terminal(s) and g.utility(s, 0) == 1 and g.utility(s, 1) == -1
    s = run((0, 2), "cr" + "f")  # P1 raises, P0 folds: P0 loses ante
    assert g.utility(s, 0) == -1
    s = run((0, 2), "cc/rf", board=4)  # round 2: P0 raises 4, P1 folds
    assert g.utility(s, 0) == 1
    s = run((0, 2), "rc/crf", board=4)  # r1 both put 3; P1 raises 4, P0 folds
    assert g.utility(s, 0) == -3 and g.utility(s, 1) == 3
    s = run((0, 2), "rc/rrf", board=4)  # P0 r, P1 r, P0 folds: loses 3 + 4
    assert g.utility(s, 0) == -7


def test_showdown_payoffs():
    assert g.utility(run((4, 0), "cc/cc", board=2), 0) == 1  # K vs J, no pair: high card
    assert g.utility(run((0, 4), "cc/cc", board=2), 0) == -1
    assert g.utility(run((0, 4), "cc/cc", board=1), 0) == 1  # J pairs board, beats K
    assert g.utility(run((0, 4), "cc/cc", board=5), 0) == -1  # K pairs board
    assert g.utility(run((0, 1), "cc/cc", board=2), 0) == 0  # same rank: tie
    # rrc/rrc: round 1 each 4, round 2 each 8, plus ante: 13 each
    s = run((0, 4), "rrc/rrc", board=1)
    assert g.utility(s, 0) == 13 and g.utility(s, 1) == -13
    assert g.utility(run((0, 4), "rc/rc", board=2), 0) == -7  # K wins; 1+2+4 = 7


def test_raise_cap_and_legal():
    s = run((0, 2), "rr")
    assert g.legal_actions(s) == ["f", "c"]
    assert g.legal_actions(run((0, 2), "r")) == ["f", "c", "r"]
    assert g.legal_actions(run((0, 2), "")) == ["c", "r"]


def test_infoset_hides_opponent():
    a = run((0, 2), "c")
    b = run((0, 4), "c")
    assert g.infoset_key(a, 0) == g.infoset_key(b, 0)
    assert g.infoset_key(a, 0) != g.infoset_key(run((2, 0), "c"), 0)
    assert g.infoset_key(run((0, 2), "cc/", board=4), 0).count("|") == 2
