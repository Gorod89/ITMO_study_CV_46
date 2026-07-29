"""Открытый CPU baseline для smoke-режима лабораторной DenseCRF.

Модуль намеренно не является качественной сегментационной моделью. Он оценивает
отличие пикселя от медианного цвета границы кадра и позволяет воспроизвести весь
контракт лабораторной без закрытых весов. В полном режиме преподаватель может
подменить реализацию классом с тем же интерфейсом.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class SegmentationResult:
    probability: np.ndarray
    mask: np.ndarray
    elapsed_seconds: float
    metadata: dict[str, Any]


class SegmentationPredictor:
    """Детерминированный baseline, работающий только на CPU."""

    def __init__(
        self,
        model_variant: str = "open-smoke",
        threshold: float = 0.5,
        temperature: float = 0.08,
    ) -> None:
        if model_variant not in {"open-smoke", "baseline"}:
            raise ValueError("Открытый provider поддерживает варианты open-smoke и baseline")
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold должен находиться между 0 и 1")
        if temperature <= 0.0:
            raise ValueError("temperature должен быть положительным")
        self.model_variant = model_variant
        self.threshold = threshold
        self.temperature = temperature

    @staticmethod
    def _border_pixels(image: np.ndarray) -> np.ndarray:
        top = image[0, :, :]
        bottom = image[-1, :, :]
        left = image[1:-1, 0, :]
        right = image[1:-1, -1, :]
        return np.concatenate([top, bottom, left, right], axis=0)

    def predict(self, image_path: str | Path) -> SegmentationResult:
        started = perf_counter()
        path = Path(image_path)
        image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0

        background = np.median(self._border_pixels(image), axis=0)
        distance = np.linalg.norm(image - background, axis=-1) / np.sqrt(3.0)
        pivot = float(np.quantile(distance, 0.65))
        logits = (distance - pivot) / self.temperature
        probability = (1.0 / (1.0 + np.exp(-np.clip(logits, -20.0, 20.0)))).astype(
            np.float32
        )
        mask = (probability >= self.threshold).astype(np.uint8)

        return SegmentationResult(
            probability=probability,
            mask=mask,
            elapsed_seconds=perf_counter() - started,
            metadata={
                "provider": "numpy-cpu",
                "model_variant": self.model_variant,
                "threshold": self.threshold,
                "temperature": self.temperature,
                "image_path": str(path),
                "warning": "Smoke baseline; не использовать как оценку качества полной модели.",
            },
        )
