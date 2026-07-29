import json
from pathlib import Path

import numpy as np
import pytest

from coursekit.experiment import ExperimentJournal


def test_journal_appends_valid_jsonl(tmp_path: Path) -> None:
    journal_path = tmp_path / "runs" / "experiments.jsonl"
    journal = ExperimentJournal(journal_path)

    first = journal.log(
        metrics={"iou": np.float32(0.75)},
        config={
            "image_size": (64, 64),
            "path": Path("data"),
            "thresholds": np.array([0.25, 0.5]),
        },
        seed=42,
        tags=["baseline", "baseline"],
        cwd=tmp_path,
    )
    journal.log(metrics={"iou": 0.8}, cwd=tmp_path)

    rows = [json.loads(line) for line in journal_path.read_text().splitlines()]
    assert len(rows) == 2
    assert rows[0]["run_id"] == first["run_id"]
    assert rows[0]["config"]["image_size"] == [64, 64]
    assert rows[0]["config"]["thresholds"] == [0.25, 0.5]
    assert rows[0]["tags"] == ["baseline"]


def test_journal_rejects_non_finite_metrics(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="конечными"):
        ExperimentJournal(tmp_path / "runs.jsonl").log(metrics={"loss": float("nan")})
