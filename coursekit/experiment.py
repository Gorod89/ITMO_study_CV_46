"""Журнал экспериментов в переносимом формате JSON Lines."""

from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _git_state(cwd: Path) -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
                timeout=3,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            return None
        return result.stdout.strip()

    commit = run("rev-parse", "HEAD")
    status = run("status", "--porcelain")
    return {"commit": commit, "dirty": bool(status) if status is not None else None}


def _json_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if hasattr(value, "tolist") and callable(value.tolist):
        return _json_value(value.tolist())
    if hasattr(value, "item") and callable(value.item):
        return _json_value(value.item())
    return value


class ExperimentJournal:
    """Дописываемый журнал, пригодный для Git, pandas и командной проверки."""

    def __init__(self, path: str | Path = "runs/experiments.jsonl") -> None:
        self.path = Path(path)

    def log(
        self,
        *,
        metrics: Mapping[str, float],
        config: Mapping[str, Any] | None = None,
        seed: int | None = None,
        tags: list[str] | None = None,
        cwd: str | Path = ".",
    ) -> dict[str, Any]:
        """Добавить одну запись и вернуть её как словарь."""
        normalized_metrics = {str(key): float(value) for key, value in metrics.items()}
        if any(not math.isfinite(value) for value in normalized_metrics.values()):
            raise ValueError("Все метрики должны быть конечными числами")

        working_directory = Path(cwd).resolve()
        record = {
            "run_id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "seed": seed,
            "tags": sorted(set(tags or [])),
            "config": _json_value(config or {}),
            "metrics": normalized_metrics,
            "environment": {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "executable": sys.executable,
                "git": _git_state(working_directory),
            },
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return record
