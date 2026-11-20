"""Scripted terminal play: full Kuhn/Leduc hands via injected input, invalid input reprompts."""
import re

import pytest

from play.cli import run


def auto_input(log):
    """Answer each prompt with the first legal action listed in it; log the prompts."""
    def inp(prompt):
        log.append(prompt)
        return re.findall(r"(\w)=", prompt)[0]
    return inp


def scripted_input(answers, log):
    """Feed fixed answers in order, then fall back to the first legal action."""
    queue = list(answers)
    fallback = auto_input(log)

    def inp(prompt):
        if queue:
            log.append(prompt)
            return queue.pop(0)
        return fallback(prompt)
    return inp


def results(lines):
    return [float(x.split("Result: ")[1].split(" chips")[0]) for x in lines if x.startswith("Result: ")]


@pytest.mark.parametrize("game", ["kuhn", "leduc"])
def test_full_hands_scripted(game):
    out_lines, prompts = [], []
    total = run(game, seed=3, hands=4, inp=auto_input(prompts), out=out_lines.append)
    # four complete hands, seats alternate 0,1,0,1
    assert [l for l in out_lines if l.startswith("--- Hand")] == [
        "--- Hand %d (you are player %d) ---" % (h + 1, h % 2) for h in range(4)]
    assert sum(1 for l in out_lines if l.startswith("History: ")) == 4
    # bot acted and showed its probabilities each time
    assert any(l.startswith("Bot plays ") and "Its strategy here:" in l for l in out_lines)
    # each hand's chip result is a legal payoff; running total matches the sum of results
    r = results(out_lines)
    assert len(r) == 4
    assert all(abs(x) <= (2 if game == "kuhn" else 13) for x in r)
    assert total == pytest.approx(sum(r))
    assert any("Running total: " + format(total, "+g") in l for l in out_lines)
    assert prompts  # human was actually prompted


def test_kuhn_hand_payoff_is_ante_scale():
    # a single Kuhn hand: payoffs are +-1 (ante only) or +-2 (one bet called)
    out_lines = []
    total = run("kuhn", seed=0, hands=1, inp=auto_input([]), out=out_lines.append)
    assert total in (-2.0, -1.0, 1.0, 2.0)


def test_invalid_input_reprompts():
    out_lines, prompts = [], []
    inp = scripted_input(["zzz", "", "?"], prompts)
    total = run("kuhn", seed=1, hands=1, inp=inp, out=out_lines.append)
    invalid = [l for l in out_lines if l.startswith("Invalid input")]
    assert invalid == ["Invalid input 'zzz'.", "Invalid input ''.", "Invalid input '?'."]
    # reprompted each time before the valid answer; hand still completed
    assert len(results(out_lines)) == 1
    assert total == pytest.approx(results(out_lines)[0])


def test_invalid_input_not_legal_for_leduc_reprompts():
    # 'p' is never a Leduc action, so it must be rejected
    out_lines = []
    inp = scripted_input(["p"], [])
    run("leduc", seed=2, hands=1, inp=inp, out=out_lines.append)
    assert "Invalid input 'p'." in out_lines
    assert len(results(out_lines)) == 1
