"""Texas Hold'em preflop hand classes: 169 classes from 1326 two-card combos.

A class is a hand type up to suit relabelling:
  - pair    e.g. "AA"   : 6 combos
  - suited  e.g. "AKs"  : 4 combos (both cards same suit)
  - offsuit e.g. "AKo"  : 12 combos (different suits)

Cards are two-character strings: rank + lowercase suit, e.g. "Ah", "Td", "2c".
Ranks are "23456789TJQKA" (2 lowest). Suits are "cdhs".

Grid layout (standard 13x13 chart): rows and columns are indexed by rank with
A = 0 ... 2 = 12. Pairs sit on the diagonal, suited hands in the upper triangle
(row = high rank, col = low rank), offsuit hands in the lower triangle
(row = low rank, col = high rank).
"""

from itertools import combinations

RANKS = "23456789TJQKA"
SUITS = "cdhs"

# Index used for the chart: A = 0, K = 1, ..., 2 = 12.
_CHART_INDEX = {r: 12 - RANKS.index(r) for r in RANKS}


def _label(hi: str, lo: str, kind: str) -> str:
    if kind == "pair":
        return hi + lo
    return hi + lo + ("s" if kind == "suited" else "o")


def _build_classes():
    """All 169 class labels, ordered pairs, suited, offsuit (each by high rank desc)."""
    labels = []
    desc = RANKS[::-1]
    for i, hi in enumerate(desc):
        labels.append(_label(hi, hi, "pair"))
    for i, hi in enumerate(desc):
        for lo in desc[i + 1:]:
            labels.append(_label(hi, lo, "suited"))
    for i, hi in enumerate(desc):
        for lo in desc[i + 1:]:
            labels.append(_label(hi, lo, "offsuit"))
    return tuple(labels)


HAND_CLASSES = _build_classes()
CLASS_INDEX = {lab: i for i, lab in enumerate(HAND_CLASSES)}


def class_type(label: str) -> str:
    """Return 'pair', 'suited' or 'offsuit' for a class label."""
    if len(label) == 2:
        return "pair"
    if label.endswith("s"):
        return "suited"
    if label.endswith("o"):
        return "offsuit"
    raise ValueError(f"bad hand class label: {label!r}")


def class_ranks(label: str):
    """Return (high_rank, low_rank) characters of a class label."""
    if label not in CLASS_INDEX:
        raise ValueError(f"unknown hand class: {label!r}")
    return label[0], label[1]


def class_combos(label: str):
    """All two-card combos of a class as tuples (card1, card2)."""
    hi, lo = class_ranks(label)
    kind = class_type(label)
    combos = []
    if kind == "pair":
        for s1, s2 in combinations(SUITS, 2):
            combos.append((hi + s1, lo + s2))
    elif kind == "suited":
        for s in SUITS:
            combos.append((hi + s, lo + s))
    else:
        for s1 in SUITS:
            for s2 in SUITS:
                if s1 != s2:
                    combos.append((hi + s1, lo + s2))
    return combos


def class_grid_position(label: str):
    """(row, col) on the 13x13 chart, A = 0 ... 2 = 12."""
    hi, lo = class_ranks(label)
    kind = class_type(label)
    h, l = _CHART_INDEX[hi], _CHART_INDEX[lo]
    if kind == "pair":
        return (h, h)
    if kind == "suited":
        return (min(h, l), max(h, l))
    return (max(h, l), min(h, l))


def hand_label(card1: str, card2: str) -> str:
    """Class label for two concrete cards, e.g. ('Ah', 'Kd') -> 'AKo'."""
    for c in (card1, card2):
        if len(c) != 2 or c[0] not in RANKS or c[1] not in SUITS:
            raise ValueError(f"bad card: {c!r}")
    if card1 == card2:
        raise ValueError("cards must be distinct")
    a, b = sorted((card1, card2), key=lambda c: RANKS.index(c[0]), reverse=True)
    if a[0] == b[0]:
        return _label(a[0], b[0], "pair")
    return _label(a[0], b[0], "suited" if a[1] == b[1] else "offsuit")
