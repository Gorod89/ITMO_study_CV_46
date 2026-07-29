"""Небольшой набор эталонных метрик для бинарной сегментации."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _binary_masks(y_true: ArrayLike, y_pred: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    true = np.asarray(y_true, dtype=bool)
    pred = np.asarray(y_pred, dtype=bool)
    if true.shape != pred.shape:
        raise ValueError(f"Формы масок различаются: {true.shape} != {pred.shape}")
    if true.size == 0:
        raise ValueError("Маски не должны быть пустыми")
    return true, pred


def intersection_over_union(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Вычислить IoU; для двух пустых масок вернуть 1.0."""
    true, pred = _binary_masks(y_true, y_pred)
    intersection = np.logical_and(true, pred).sum(dtype=np.int64)
    union = np.logical_or(true, pred).sum(dtype=np.int64)
    return 1.0 if union == 0 else float(intersection / union)


def dice_score(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Вычислить коэффициент Dice; для двух пустых масок вернуть 1.0."""
    true, pred = _binary_masks(y_true, y_pred)
    intersection = np.logical_and(true, pred).sum(dtype=np.int64)
    denominator = true.sum(dtype=np.int64) + pred.sum(dtype=np.int64)
    return 1.0 if denominator == 0 else float(2 * intersection / denominator)
