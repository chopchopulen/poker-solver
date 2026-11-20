"""Query push/fold equilibrium: python -m play.pushfold --stack 10 --hand AJo"""
import argparse
import csv
import os
import sys

DEFAULT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "analysis", "pushfold_ranges.csv")


def load(path=DEFAULT_CSV):
    """{(stack, hand): (shove, call)}"""
    table = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            table[(int(row["stack"]), row["hand"])] = (float(row["shove"]), float(row["call"]))
    return table


def normalize_hand(h):
    """'ajo' -> 'AJo', 'aa' -> 'AA', 'JAo' -> 'AJo'. Returns None if malformed."""
    ranks = "23456789TJQKA"
    h = h.strip()
    if len(h) not in (2, 3):
        return None
    a, b = h[0].upper(), h[1].upper()
    if a not in ranks or b not in ranks:
        return None
    if a == b:
        return a + b if len(h) == 2 else None
    if len(h) != 3 or h[2].lower() not in "so":
        return None
    if ranks.index(a) < ranks.index(b):
        a, b = b, a
    return a + b + h[2].lower()


def query(stack, hand, table):
    return table[(stack, hand)]


def main(argv=None):
    p = argparse.ArgumentParser(prog="play.pushfold")
    p.add_argument("--stack", type=int, required=True, help="effective stack in BB (1-20)")
    p.add_argument("--hand", required=True, help="hand class, e.g. AJo, KQs, 77")
    p.add_argument("--csv", default=DEFAULT_CSV)
    args = p.parse_args(argv)
    if not 1 <= args.stack <= 20:
        print(f"error: stack must be an integer in 1..20, got {args.stack}", file=sys.stderr)
        return 2
    hand = normalize_hand(args.hand)
    if hand is None:
        print(f"error: bad hand {args.hand!r} (use e.g. AA, AKs, AJo)", file=sys.stderr)
        return 2
    table = load(args.csv)
    if (args.stack, hand) not in table:
        print(f"error: no data for stack {args.stack} hand {hand}", file=sys.stderr)
        return 2
    shove, call = query(args.stack, hand, table)
    print(f"stack={args.stack}BB hand={hand}: SB shove {shove:.4f}, BB call {call:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
