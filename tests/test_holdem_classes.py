from collections import Counter
from itertools import combinations

from games.holdem_classes import (
    CLASS_INDEX,
    HAND_CLASSES,
    RANKS,
    SUITS,
    class_combos,
    class_grid_position,
    class_type,
    hand_label,
)


def test_169_unique_classes():
    assert len(HAND_CLASSES) == 169
    assert len(set(HAND_CLASSES)) == 169
    assert Counter(class_type(c) for c in HAND_CLASSES) == {
        "pair": 13,
        "suited": 78,
        "offsuit": 78,
    }


def test_combo_counts_per_type():
    for lab in HAND_CLASSES:
        n = len(class_combos(lab))
        expected = {"pair": 6, "suited": 4, "offsuit": 12}[class_type(lab)]
        assert n == expected, lab


def test_combos_sum_to_1326_and_are_distinct():
    all_combos = [frozenset(c) for lab in HAND_CLASSES for c in class_combos(lab)]
    assert len(all_combos) == 1326
    assert len(set(all_combos)) == 1326
    # every combo of the full deck appears exactly once
    deck = [r + s for r in RANKS for s in SUITS]
    assert set(all_combos) == {frozenset(p) for p in combinations(deck, 2)}


def test_combos_map_back_to_their_class():
    for lab in HAND_CLASSES:
        for c1, c2 in class_combos(lab):
            assert hand_label(c1, c2) == lab


def test_grid_covers_169_cells_once():
    cells = [class_grid_position(lab) for lab in HAND_CLASSES]
    assert len(set(cells)) == 169
    assert set(cells) == {(r, c) for r in range(13) for c in range(13)}


def test_grid_layout_convention():
    assert class_grid_position("AA") == (0, 0)
    assert class_grid_position("22") == (12, 12)
    assert class_grid_position("AKs") == (0, 1)  # upper triangle
    assert class_grid_position("AKo") == (1, 0)  # lower triangle
    assert class_grid_position("72o") == (12, 7)  # 7 -> col 7, 2 -> row 12


def test_class_index_round_trip():
    for i, lab in enumerate(HAND_CLASSES):
        assert CLASS_INDEX[lab] == i


def test_hand_label_examples():
    assert hand_label("Ah", "Kd") == "AKo"
    assert hand_label("Kd", "Ah") == "AKo"
    assert hand_label("Ah", "Kh") == "AKs"
    assert hand_label("7c", "7d") == "77"
