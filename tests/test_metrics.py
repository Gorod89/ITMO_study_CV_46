import numpy as np
import pytest

from coursekit.metrics import dice_score, intersection_over_union


def test_binary_segmentation_metrics() -> None:
    truth = np.array([[1, 1], [0, 0]])
    prediction = np.array([[1, 0], [1, 0]])

    assert intersection_over_union(truth, prediction) == pytest.approx(1 / 3)
    assert dice_score(truth, prediction) == pytest.approx(0.5)


def test_two_empty_masks_are_a_perfect_match() -> None:
    empty = np.zeros((2, 2), dtype=np.uint8)
    assert intersection_over_union(empty, empty) == 1.0
    assert dice_score(empty, empty) == 1.0


def test_different_shapes_are_rejected() -> None:
    with pytest.raises(ValueError, match="Формы"):
        dice_score(np.zeros((2, 2)), np.zeros((4,)))
