import json
import os

from agents.adaptive import AdaptiveAgent
from agents.bots import AlwaysCall
from agents.exploiter import Exploiter, bot_strategy
from eval.match import _play
from games.leduc import LeducPoker
from tests.test_equilibrium_agent import ROOT, decision_states

G = LeducPoker()
STATES = decision_states(G)
EQ = json.load(open(os.path.join(ROOT, "analysis/strategies/leduc.json")))


def freqs(agent):
    """Exact action probs per infoset from the agent's current policy."""
    out = {}
    for s in STATES:
        k = G.infoset_key(s, G.current_player(s))
        legal = list(G.legal_actions(s))
        out[k] = dict(zip(legal, agent.policy(G.current_player(s), k, legal)))
    return out


def opp_only_calls(key, seat):
    """True if every opponent action in the key's history is 'c' (reachable vs AlwaysCall)."""
    hist, rl = key.split("|")[2], 0
    for ch in hist:
        if ch == "/":
            rl = 0
            continue
        if rl % 2 != seat and ch != "c":
            return False
        rl += 1
    return True


def dist_to(freq, target):
    return sum(abs(freq[k][a] - target[k].get(a, 0.0)) for k in freq for a in freq[k]) / len(freq)


def test_no_observations_is_equilibrium():
    ag = AdaptiveAgent(G, EQ, seed=3)
    f = freqs(ag)
    assert ag.n == 0 and ag.weight() == 0
    assert dist_to(f, EQ) < 1e-9


def test_moves_toward_exploiter_after_always_call():
    ag = AdaptiveAgent(G, EQ, seed=1, refresh=10)
    bot = AlwaysCall()
    for i in range(400):  # no reset(): agent keeps its model across hands
        _play(G, (ag, bot), i)
        _play(G, (bot, ag), i)
    assert ag.n > 0 and ag.weight() > 0.5
    for seat in (0, 1):
        ex = Exploiter(G, bot_strategy(G, bot, STATES), seat)
        tgt = {}
        for s in STATES:
            if G.current_player(s) == seat:
                k = G.infoset_key(s, seat)
                a = ex.act(G, s, k)
                tgt[k] = {x: float(x == a) for x in G.legal_actions(s)}
        f = {k: v for k, v in freqs(ag).items() if k in tgt and opp_only_calls(k, seat)}
        tgt = {k: tgt[k] for k in f}
        assert dist_to(f, tgt) < dist_to(f, EQ)


def test_safe_vs_equilibrium():
    """Capped exploitation weight => adaptive loses < 50 mbb/hand (95% CI lower bound) to equilibrium.
    Needs ~16k mirrored pairs for a CI this tight (Leduc pair std ~2.2 chips); ~25s, deterministic seeds."""
    from agents.equilibrium import EquilibriumAgent
    from eval.match import play_match
    r = play_match(G, AdaptiveAgent(G, EQ, seed=1, cap=0.2), EquilibriumAgent(EQ, seed=2), 16000, seed=5)
    assert r["lo_mbb"] > -50, r
