import pytest
from games.base import Game

METHODS = {
    "initial_state": lambda self: None,
    "is_terminal": lambda self, s: True,
    "is_chance": lambda self, s: False,
    "chance_outcomes": lambda self, s: [],
    "current_player": lambda self, s: 0,
    "legal_actions": lambda self, s: [],
    "next_state": lambda self, s, a: s,
    "utility": lambda self, s, p: 0.0,
    "infoset_key": lambda self, s, p: "",
}


def test_abstract_game_not_instantiable():
    with pytest.raises(TypeError):
        Game()


@pytest.mark.parametrize("missing", sorted(METHODS))
def test_subclass_missing_method_not_instantiable(missing):
    attrs = {k: v for k, v in METHODS.items() if k != missing}
    with pytest.raises(TypeError):
        type("Partial", (Game,), attrs)()


def test_complete_subclass_instantiates():
    type("Full", (Game,), dict(METHODS))()
