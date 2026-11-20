import pytest

from games.market_making import MarketMakingGame, MMConfig


def test_default_config_validates():
    cfg = MMConfig().validate()
    assert cfg.deck_size == 10
    assert cfg.taker_sees == 1
    assert cfg.rounds == 1


def test_game_accepts_default_and_none():
    assert MarketMakingGame().config == MarketMakingGame(MMConfig()).config


@pytest.mark.parametrize(
    "kwargs",
    [
        {"deck_size": 2},
        {"taker_sees": 3},
        {"taker_sees": -1},
        {"rounds": 0},
        {"rounds": 3},
        {"mids": ()},
        {"spreads": ()},
        {"spreads": (1, 0)},
        {"spreads": (-2,)},
        {"noise_prob": -0.1},
        {"noise_prob": 1.5},
    ],
)
def test_bad_config_raises(kwargs):
    with pytest.raises(ValueError):
        MMConfig(**kwargs).validate()


def test_game_rejects_bad_config():
    with pytest.raises(ValueError):
        MarketMakingGame(MMConfig(taker_sees=5))


def _game(**kw):
    kw.setdefault("deck_size", 5)
    kw.setdefault("mids", (6, 9))
    kw.setdefault("spreads", (2, 4))
    return MarketMakingGame(MMConfig(**kw))


def _terminal(g, cards, noise, quote, act):
    s = g.initial_state()
    for a in (cards, noise, quote, act):
        s = g.next_state(s, a)
    return s


def test_chance_probs_sum_to_one():
    g = _game()
    s = g.initial_state()
    assert g.is_chance(s)
    outs = g.chance_outcomes(s)
    assert len(outs) == 5 * 4 * 3 and abs(sum(p for _, p in outs) - 1) < 1e-12
    s = g.next_state(s, outs[0][0])
    assert g.is_chance(s) and abs(sum(p for _, p in g.chance_outcomes(s)) - 1) < 1e-12
    s = g.next_state(s, True)
    assert not g.is_chance(s) and g.current_player(s) == 0
    s = g.next_state(s, 0)  # noise trader -> uniform chance over b/s/p
    assert g.is_chance(s) and abs(sum(p for _, p in g.chance_outcomes(s)) - 1) < 1e-12
    s2 = g.next_state(g.next_state(g.next_state(g.initial_state(), (1, 2, 3)), False), 0)
    assert not g.is_chance(s2) and g.current_player(s2) == 1  # informed taker decides


def test_payoffs_buy_sell_pass():
    g = _game()
    assert g.quote(0) == (5, 7)  # mid 6, spread 2; V = 1+2+3 = 6
    b = _terminal(g, (1, 2, 3), False, 0, "b")
    assert g.is_terminal(b) and g.utility(b, 1) == 6 - 7 and g.utility(b, 0) == 1
    s = _terminal(g, (1, 2, 3), False, 0, "s")
    assert g.utility(s, 1) == 5 - 6 and g.utility(s, 0) == 1
    p = _terminal(g, (1, 2, 3), True, 0, "p")
    assert g.utility(p, 0) == g.utility(p, 1) == 0
    # V=12, quote 3 = mid 9 spread 4 -> bid 7, ask 11
    assert g.utility(_terminal(g, (3, 4, 5), False, 3, "b"), 1) == 1
    assert g.utility(_terminal(g, (3, 4, 5), False, 3, "s"), 1) == -5


def test_zero_sum_everywhere():
    g = _game()
    for q in range(4):
        for a in "bsp":
            t = _terminal(g, (2, 5, 1), True, q, a)
            assert g.utility(t, 0) + g.utility(t, 1) == 0


def test_keys_hide_unseen_cards():
    def key(see, cards):
        g = _game(taker_sees=see)
        s = g.next_state(g.next_state(g.next_state(g.initial_state(), cards), False), 1)
        return g.infoset_key(s, 1), g.infoset_key(s, 0)

    assert key(0, (1, 2, 3))[0] == key(0, (4, 5, 1))[0]  # taker sees nothing
    assert key(1, (1, 2, 3))[0] == key(1, (4, 2, 5))[0]  # own card only
    assert key(1, (1, 2, 3))[0] != key(1, (1, 3, 2))[0]
    assert key(2, (1, 2, 3))[0] != key(2, (1, 2, 4))[0]  # hidden visible
    assert key(2, (1, 2, 3))[0] == key(2, (5, 2, 3))[0]  # MM card never visible
    assert key(1, (1, 2, 3))[1] == key(1, (1, 4, 5))[1]  # MM sees only own card
    assert key(1, (1, 2, 3))[1] != key(1, (2, 1, 3))[1]


def _count(g, s):
    if g.is_terminal(s):
        return 1
    acts = [a for a, _ in g.chance_outcomes(s)] if g.is_chance(s) else g.legal_actions(s)
    return sum(_count(g, g.next_state(s, a)) for a in acts)


def test_rounds2_tree_shape():
    g = _game(rounds=2, deck_size=3, mids=(6,), spreads=(2, 4))
    s = g.next_state(g.next_state(g.initial_state(), (1, 2, 3)), False)
    assert g.current_player(s) == 0 and not g.is_chance(s)
    s = g.next_state(s, 0)
    assert g.current_player(s) == 1 and not g.is_terminal(s)
    s = g.next_state(s, "b")
    assert not g.is_terminal(s) and g.current_player(s) == 0  # MM requotes
    s = g.next_state(s, 1)
    assert g.current_player(s) == 1
    t = g.next_state(s, "s")
    assert g.is_terminal(t) and g.utility(t, 0) + g.utility(t, 1) == 0
    # V=6: round 1 quote 0 (5,7) buy -> -1; round 2 quote 1 (4,8) sell -> 4-6 = -2
    assert g.utility(t, 1) == (6 - 7) + (4 - 6)
    # 6 deals x 2 noise types x (2 quotes x 3 acts)^2
    assert _count(g, g.initial_state()) == 6 * 2 * 36


def test_rounds2_keys_visibility():
    g = _game(rounds=2, taker_sees=1)

    def at(cards, q1, a1, q2=None):
        s = g.next_state(g.next_state(g.initial_state(), cards), False)
        s = g.next_state(g.next_state(s, q1), a1)
        return s if q2 is None else g.next_state(s, q2)

    m1, m2 = at((1, 2, 3), 0, "b"), at((1, 4, 5), 0, "b")
    assert g.infoset_key(m1, 0) == g.infoset_key(m2, 0)  # MM: own card + history only
    assert g.infoset_key(m1, 0) != g.infoset_key(at((1, 2, 3), 0, "s"), 0)
    t1, t2 = at((1, 2, 3), 0, "b", 1), at((4, 2, 5), 0, "b", 1)
    assert g.infoset_key(t1, 1) == g.infoset_key(t2, 1)  # taker sees own card only
    assert g.infoset_key(t1, 1) != g.infoset_key(at((1, 2, 3), 0, "b", 2), 1)


def test_mm_solve_small_deck_converges():
    from scripts.mm_solve import solve
    cfg = MMConfig(deck_size=5, mids=(6, 9), spreads=(1, 3))
    _, _, rows = solve(cfg, 300, npoints=3)
    assert rows[-1][2] < 0.01
