"""Mirrored head-to-head matches. Each pair = same deal played twice with seats swapped;
the per-pair mean of agent A's chips is the sample (cancels card luck)."""
import math

import numpy as np


def _play(game, agents, chance_seed):
    """Play one hand. All chance outcomes come from a fresh RNG seeded by chance_seed,
    so the same seed gives the same cards in both seatings. Returns (u_seat0, u_seat1)."""
    rng = np.random.default_rng(chance_seed)
    s = game.initial_state()
    while not game.is_terminal(s):
        if game.is_chance(s):
            outs = game.chance_outcomes(s)
            a = outs[rng.choice(len(outs), p=[p for _, p in outs])][0]
        else:
            p = game.current_player(s)
            a = agents[p].act(game, s, game.infoset_key(s, p))
            assert a in game.legal_actions(s), "illegal action"
        s = game.next_state(s, a)
    for p in (0, 1):
        agents[p].observe_end(game, s[2], p)  # public history only
    return game.utility(s, 0), game.utility(s, 1)


def play_match(game, agent_a, agent_b, n_pairs, seed=0):
    """Play n_pairs mirrored pairs (2*n_pairs hands). Returns dict: mean chips/hand for A,
    mbb/hand (1 chip = 1 bb = ante), 95% CI half-width (normal approx over pairs)."""
    rng = np.random.default_rng(seed)
    agent_a.reset()
    agent_b.reset()
    vals = np.empty(n_pairs)
    for i in range(n_pairs):
        sub = int(rng.integers(2**31))
        a0 = _play(game, (agent_a, agent_b), sub)[0]
        a1 = _play(game, (agent_b, agent_a), sub)[1]
        vals[i] = 0.5 * (a0 + a1)
    mean = float(vals.mean())
    hw = 1.96 * float(vals.std(ddof=1)) / math.sqrt(n_pairs) if n_pairs > 1 else float("nan")
    return {"mean": mean, "mbb": 1000 * mean, "ci": hw, "ci_mbb": 1000 * hw,
            "lo_mbb": 1000 * (mean - hw), "hi_mbb": 1000 * (mean + hw),
            "n_hands": 2 * n_pairs}
