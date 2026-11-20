import csv
import subprocess
import sys

from play.pushfold import main, normalize_hand, DEFAULT_CSV


def _row(stack, hand):
    with open(DEFAULT_CSV) as f:
        for r in csv.DictReader(f):
            if int(r["stack"]) == stack and r["hand"] == hand:
                return float(r["shove"]), float(r["call"])


def test_matches_csv(capsys):
    assert main(["--stack", "10", "--hand", "ajo"]) == 0
    out = capsys.readouterr().out
    s, c = _row(10, "AJo")
    assert f"{s:.4f}" in out and f"{c:.4f}" in out and "AJo" in out


def test_normalize():
    assert normalize_hand("JAo") == "AJo"
    assert normalize_hand("77") == "77"
    for bad in ["", "AJ", "AAo", "XYo", "AJx", "AJoo"]:
        assert normalize_hand(bad) is None


def test_rejects_bad(capsys):
    assert main(["--stack", "0", "--hand", "AA"]) == 2
    assert main(["--stack", "21", "--hand", "AA"]) == 2
    assert main(["--stack", "10", "--hand", "ZZ"]) == 2


def test_subprocess():
    r = subprocess.run([sys.executable, "-m", "play.pushfold", "--stack", "10", "--hand", "AJo"],
                       capture_output=True, text=True)
    s, c = _row(10, "AJo")
    assert r.returncode == 0 and f"{s:.4f}" in r.stdout and f"{c:.4f}" in r.stdout
