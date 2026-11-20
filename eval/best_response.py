"""Exact best response of one player against a fixed strategy profile."""


def best_response(game, strategies, player):
    """Return (value, best): best maps player infoset key -> action.

    Value to `player` of best-responding to strategies[1-player].

    strategies: [strat0, strat1], each key -> {action: prob}. Only strategies[1-player] is used.
    Infoset-level: each infoset of `player` gets ONE action, chosen by summing over every
    state in it (weighted by opponent*chance reach), so the BR never peeks at hidden cards.
    """
    opp = 1 - player
    opp_strat = strategies[opp]

    # pass 1: group player's states by infoset with weight = opp reach * chance reach
    groups = {}

    def collect(state, w):
        if game.is_terminal(state):
            return
        if game.is_chance(state):
            for a, p in game.chance_outcomes(state):
                collect(game.next_state(state, a), w * p)
            return
        pl = game.current_player(state)
        if pl == player:
            groups.setdefault(game.infoset_key(state, pl), []).append((state, w))
            for a in game.legal_actions(state):
                collect(game.next_state(state, a), w)
        else:
            probs = opp_strat[game.infoset_key(state, pl)]
            for a in game.legal_actions(state):
                collect(game.next_state(state, a), w * probs[a])

    collect(game.initial_state(), 1.0)

    # pass 2: lazily pick best action per infoset (deeper infosets resolved recursively)
    best = {}

    def value(state):
        if game.is_terminal(state):
            return game.utility(state, player)
        if game.is_chance(state):
            return sum(p * value(game.next_state(state, a))
                       for a, p in game.chance_outcomes(state))
        pl = game.current_player(state)
        key = game.infoset_key(state, pl)
        if pl == opp:
            probs = opp_strat[key]
            return sum(probs[a] * value(game.next_state(state, a))
                       for a in game.legal_actions(state))
        if key not in best:
            best[key] = max(
                game.legal_actions(state),
                key=lambda a: sum(w * value(game.next_state(s, a)) for s, w in groups[key]))
        return value(game.next_state(state, best[key]))

    v = value(game.initial_state())
    return v, best


def best_response_value(game, strategies, player):
    return best_response(game, strategies, player)[0]
