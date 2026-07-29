import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dependency_names(requirements: list[str]) -> set[str]:
    return {
        re.split(r"[\s<>=!~\[]", requirement, maxsplit=1)[0].lower() for requirement in requirements
    }


def test_notebook_profiles_cover_direct_third_party_imports() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    extras = config["project"]["optional-dependencies"]

    cv = dependency_names(extras["cv"])
    deep_learning = dependency_names(extras["deep-learning"])
    retrieval = dependency_names(extras["retrieval"])
    inference = dependency_names(extras["inference"])
    yolo = dependency_names(extras["yolo"])

    assert {
        "matplotlib",
        "opencv-contrib-python-headless",
        "pandas",
        "scikit-image",
        "scikit-learn",
    }.issubset(cv)
    assert {
        "albumentations",
        "segmentation-models-pytorch",
        "timm",
        "torchmetrics",
        "transformers",
    }.issubset(deep_learning)
    assert {"faiss-cpu"}.issubset(retrieval)
    assert {"onnxruntime"}.issubset(inference)
    assert {"pyyaml", "ultralytics"}.issubset(yolo)
