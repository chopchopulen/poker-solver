from agents.bots import AlwaysCall, AlwaysRaise, Tight
from eval.match import play_match
from games.leduc import LeducPoker


def test_self_play_ci_contains_zero():
    r = play_match(LeducPoker(), Tight(), Tight(), 300, seed=1)
    assert r["lo_mbb"] <= 0 <= r["hi_mbb"]


def test_raise_vs_call_deterministic_per_deal():
    g = LeducPoker()
    r1 = play_match(g, AlwaysRaise(), AlwaysCall(), 200, seed=3)
    assert r1 == play_match(g, AlwaysRaise(), AlwaysCall(), 200, seed=3)
    r3 = play_match(g, AlwaysCall(), AlwaysRaise(), 200, seed=3)
    assert abs(r1["mean"] + r3["mean"]) < 1e-12  # antisymmetric


def test_mirrored_call_call_cancels():
    r = play_match(LeducPoker(), AlwaysCall(), AlwaysCall(), 100, seed=2)
    assert r["mean"] == 0.0 and r["ci"] == 0.0
