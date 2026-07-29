import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from scripts.generate_smoke_data import generate_dataset


def file_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_generator_is_byte_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    manifest = generate_dataset(first)
    generate_dataset(second)

    assert manifest["samples"] == 48
    assert file_bytes(first) == file_bytes(second)

    annotations = json.loads((first / "annotations.json").read_text(encoding="utf-8"))
    assert annotations["splits"] == {"train": 32, "validation": 8, "test": 8}
    assert len(annotations["samples"]) == 48
    mask = np.asarray(Image.open(first / annotations["samples"][0]["mask"]))
    assert set(np.unique(mask)).issubset({0, 1, 2, 3})


def test_generator_does_not_overwrite_by_default(tmp_path: Path) -> None:
    output = tmp_path / "dataset"
    generate_dataset(output)
    with pytest.raises(FileExistsError, match="--overwrite"):
        generate_dataset(output)
