import pytest

from agents.bots import AlwaysCall, AlwaysRaise, RandomBot, Tight
from games.leduc import LeducPoker
from tests.test_equilibrium_agent import decision_states

G = LeducPoker()
STATES = decision_states(G)


def key(s):
    return G.infoset_key(s, G.current_player(s))


@pytest.mark.parametrize("bot", [AlwaysCall(), AlwaysRaise(), Tight(), RandomBot(1)])
def test_legal_only(bot):
    for s in STATES:
        assert bot.act(G, s, key(s)) in G.legal_actions(s)


def test_rules():
    for s in STATES:
        k, legal = key(s), G.legal_actions(s)
        assert AlwaysCall().act(G, s, k) == "c"
        assert AlwaysRaise().act(G, s, k) == ("r" if "r" in legal else "c")
        a = Tight().act(G, s, k)
        if Tight.is_strong(k):
            assert a == ("r" if "r" in legal else "c")
        else:
            assert a == ("f" if "f" in legal else "c")


def test_random_covers_actions_and_seeded():
    s = next(x for x in STATES if len(G.legal_actions(x)) == 3)
    b = RandomBot(3)
    seq = [b.act(G, s, key(s)) for _ in range(200)]
    assert set(seq) == {"f", "c", "r"}
    b.reset()
    assert [b.act(G, s, key(s)) for _ in range(200)] == seq
