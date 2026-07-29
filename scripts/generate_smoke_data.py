#!/usr/bin/env python3
"""Создать маленький детерминированный датасет геометрических фигур."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

DEFAULT_OUTPUT = Path("data/procedural-shapes-smoke")
SPLIT_SIZES = {"train": 32, "validation": 8, "test": 8}
CLASS_NAMES = ("circle", "square", "triangle")
CLASS_COLORS = (
    np.array([225, 72, 68], dtype=np.uint8),
    np.array([64, 180, 104], dtype=np.uint8),
    np.array([70, 118, 224], dtype=np.uint8),
)


def _shape_mask(
    shape: str,
    *,
    image_size: int,
    center_x: int,
    center_y: int,
    radius: int,
) -> np.ndarray:
    yy, xx = np.mgrid[:image_size, :image_size]
    if shape == "circle":
        return (xx - center_x) ** 2 + (yy - center_y) ** 2 <= radius**2
    if shape == "square":
        return (np.abs(xx - center_x) <= radius) & (np.abs(yy - center_y) <= radius)
    if shape == "triangle":
        top = center_y - radius
        bottom = center_y + radius
        relative_y = yy - top
        half_width = radius * relative_y / max(2 * radius, 1)
        return (yy >= top) & (yy <= bottom) & (np.abs(xx - center_x) <= half_width)
    raise ValueError(f"Неизвестная фигура: {shape}")


def _sample(
    rng: np.random.Generator,
    *,
    class_id: int,
    image_size: int,
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    radius = int(rng.integers(image_size // 8, image_size // 4 + 1))
    margin = radius + 3
    center_x = int(rng.integers(margin, image_size - margin))
    center_y = int(rng.integers(margin, image_size - margin))
    shape = CLASS_NAMES[class_id]
    foreground = _shape_mask(
        shape,
        image_size=image_size,
        center_x=center_x,
        center_y=center_y,
        radius=radius,
    )

    background = rng.integers(18, 48, size=(1, 1, 3), dtype=np.uint8)
    noise = rng.integers(0, 12, size=(image_size, image_size, 3), dtype=np.uint8)
    image = np.clip(background.astype(np.uint16) + noise, 0, 255).astype(np.uint8)
    color_noise = rng.integers(0, 18, size=(image_size, image_size, 1), dtype=np.uint8)
    foreground_pixels = np.clip(
        CLASS_COLORS[class_id].astype(np.int16) + color_noise.astype(np.int16) - 9,
        0,
        255,
    ).astype(np.uint8)
    image[foreground] = foreground_pixels[foreground]

    mask = np.zeros((image_size, image_size), dtype=np.uint8)
    mask[foreground] = class_id + 1
    ys, xs = np.nonzero(foreground)
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    bbox_xywh = [x_min, y_min, x_max - x_min + 1, y_max - y_min + 1]
    return image, mask, bbox_xywh


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_dataset(target: Path, *, seed: int, image_size: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    total = sum(SPLIT_SIZES.values())
    labels = np.tile(np.arange(len(CLASS_NAMES)), (total + 2) // 3)[:total]
    rng.shuffle(labels)
    samples: list[dict[str, Any]] = []
    global_index = 0

    for split, count in SPLIT_SIZES.items():
        image_dir = target / split / "images"
        mask_dir = target / split / "masks"
        image_dir.mkdir(parents=True)
        mask_dir.mkdir(parents=True)
        for split_index in range(count):
            class_id = int(labels[global_index])
            image, mask, bbox = _sample(rng, class_id=class_id, image_size=image_size)
            sample_id = f"{split}-{split_index:04d}"
            image_relative = Path(split) / "images" / f"{sample_id}.png"
            mask_relative = Path(split) / "masks" / f"{sample_id}.png"
            Image.fromarray(image, mode="RGB").save(target / image_relative, optimize=False)
            Image.fromarray(mask, mode="L").save(target / mask_relative, optimize=False)
            samples.append(
                {
                    "id": sample_id,
                    "split": split,
                    "image": image_relative.as_posix(),
                    "mask": mask_relative.as_posix(),
                    "class_id": class_id,
                    "class_name": CLASS_NAMES[class_id],
                    "bbox_xywh": bbox,
                }
            )
            global_index += 1

    annotations = {
        "schema_version": 1,
        "dataset_id": "procedural-shapes-smoke",
        "dataset_version": "1",
        "license": "CC0-1.0",
        "seed": seed,
        "image_size": [image_size, image_size],
        "mask_values": {
            "0": "background",
            **{str(i + 1): name for i, name in enumerate(CLASS_NAMES)},
        },
        "bbox_format": "xywh, координаты пикселей, ширина и высота включают крайние пиксели",
        "classes": [{"id": class_id, "name": name} for class_id, name in enumerate(CLASS_NAMES)],
        "splits": SPLIT_SIZES,
        "samples": samples,
    }
    annotation_path = target / "annotations.json"
    annotation_path.write_text(
        json.dumps(annotations, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    files = sorted(
        path.relative_to(target)
        for path in target.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    )
    manifest = {
        "schema_version": 1,
        "dataset_id": "procedural-shapes-smoke",
        "dataset_version": "1",
        "generator": "scripts/generate_smoke_data.py",
        "seed": seed,
        "samples": total,
        "files": {relative.as_posix(): _sha256(target / relative) for relative in files},
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def generate_dataset(
    output: str | Path = DEFAULT_OUTPUT,
    *,
    seed: int = 42,
    image_size: int = 64,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Создать датасет через временный каталог и вернуть его манифест."""
    if image_size < 32:
        raise ValueError("Размер изображения должен быть не меньше 32 пикселей")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed должен быть целым числом в диапазоне [0, 2**32 - 1]")

    target = Path(output).resolve()
    unsafe_targets = {Path.cwd().resolve(), Path.home().resolve(), Path(target.anchor)}
    if target in unsafe_targets or (target / ".git").exists():
        raise ValueError("Нельзя использовать корневой, домашний каталог или Git-репозиторий")
    if target.exists() and not overwrite:
        raise FileExistsError(
            f"Каталог уже существует: {target}. Используйте --overwrite для пересоздания."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent))
    try:
        manifest = _write_dataset(temporary, seed=seed, image_size=image_size)
        if target.exists():
            if target.is_symlink() or not target.is_dir():
                raise ValueError("Перезаписывать можно только обычный каталог")
            shutil.rmtree(target)
        temporary.replace(target)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Каталог результата")
    parser.add_argument("--seed", type=int, default=42, help="Seed генератора")
    parser.add_argument("--image-size", type=int, default=64, help="Сторона изображения")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Заменить существующий каталог после успешной генерации",
    )
    args = parser.parse_args(argv)

    manifest = generate_dataset(
        args.output,
        seed=args.seed,
        image_size=args.image_size,
        overwrite=args.overwrite,
    )
    print(
        f"Создан {args.output}: {manifest['samples']} изображений, "
        f"seed={manifest['seed']}, лицензия CC0-1.0"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
