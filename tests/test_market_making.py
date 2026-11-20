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


def test_stub_methods_not_implemented():
    g = MarketMakingGame()
    with pytest.raises(NotImplementedError):
        g.initial_state()
