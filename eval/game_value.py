"""Expected value of a strategy profile."""


def game_value(game, strategies, player=0):
    """Expected payoff to `player`. strategies: [strat0, strat1], each key -> {action: prob}."""
    def walk(state):
        if game.is_terminal(state):
            return game.utility(state, player)
        if game.is_chance(state):
            return sum(p * walk(game.next_state(state, a))
                       for a, p in game.chance_outcomes(state))
        pl = game.current_player(state)
        probs = strategies[pl][game.infoset_key(state, pl)]
        return sum(probs[a] * walk(game.next_state(state, a))
                   for a in game.legal_actions(state))
    return walk(game.initial_state())
