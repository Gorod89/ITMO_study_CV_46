#!/usr/bin/env python3
"""Проверить открытый путь данные → provider → метрика без сети и GPU."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from coursekit import intersection_over_union  # noqa: E402
from scripts.generate_smoke_data import generate_dataset  # noqa: E402

PROVIDER_PATH = (
    ROOT / "block4_up_to_date_CV" / "methodical-guidelines" / "students" / "lab_segmentation.py"
)


def _load_provider():
    spec = importlib.util.spec_from_file_location("open_lab_segmentation", PROVIDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Не удалось загрузить provider: {PROVIDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.SegmentationPredictor


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cv-course-smoke-") as directory:
        data_root = Path(directory) / "procedural-shapes"
        manifest = generate_dataset(data_root, seed=42)
        image_path = next((data_root / "test" / "images").glob("*.png"))
        mask_path = data_root / "test" / "masks" / image_path.name

        predictor_class = _load_provider()
        result = predictor_class(model_variant="open-smoke").predict(image_path)
        target = np.asarray(Image.open(mask_path), dtype=np.uint8) > 0
        iou = intersection_over_union(target, result.mask)

        if result.probability.shape != target.shape:
            raise AssertionError("Provider изменил пространственный размер")
        if not np.isfinite(result.probability).all():
            raise AssertionError("Вероятностная карта содержит NaN/Inf")
        if not 0.0 <= float(result.probability.min()) <= float(result.probability.max()) <= 1.0:
            raise AssertionError("Вероятности вышли за диапазон [0, 1]")

        print(
            "Open smoke пройден:",
            f"samples={manifest['samples']}",
            f"provider={result.metadata['provider']}",
            f"iou_fixture={iou:.3f}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
