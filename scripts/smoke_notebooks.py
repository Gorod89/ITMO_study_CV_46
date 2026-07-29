#!/usr/bin/env python3
"""Исполнить только явно помеченные smoke-ноутбуки без сохранения результата."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_notebooks import discover_notebooks  # noqa: E402


def is_marked_for_smoke(path: Path) -> bool:
    """Проверить metadata.course_ci.smoke без исполнения кода."""
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return notebook.get("metadata", {}).get("course_ci", {}).get("smoke") is True


def selected_notebooks(paths: list[Path], root: Path = ROOT) -> list[Path]:
    """Явные пути исполняются всегда; без путей выбираются только помеченные."""
    if paths:
        return discover_notebooks(paths)
    return [path for path in discover_notebooks([root]) if is_marked_for_smoke(path)]


def execute_notebook(path: Path, *, timeout: int) -> None:
    """Исполнить ноутбук в памяти, не меняя исходный файл."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError as error:
        raise RuntimeError(
            "Установите группу notebooks: uv sync --group notebooks --extra cv"
        ) from error

    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=notebook.metadata.get("kernelspec", {}).get("name", "python3"),
        allow_errors=False,
        resources={"metadata": {"path": str(path.parent.resolve())}},
    )
    client.execute()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Явно выбранные ноутбуки")
    parser.add_argument("--timeout", type=int, default=180, help="Тайм-аут одной ячейки")
    args = parser.parse_args(argv)

    notebooks = selected_notebooks(args.paths)
    if not notebooks:
        print(
            "Smoke-ноутбуки не выбраны. Добавьте metadata.course_ci.smoke=true "
            "или передайте путь явно."
        )
        return 0

    os.environ["COURSE_SMOKE"] = "1"
    failures = 0
    for path in notebooks:
        print(f"SMOKE: {path}")
        try:
            execute_notebook(path, timeout=args.timeout)
        except Exception as error:
            failures += 1
            print(f"ОШИБКА: {path}: {type(error).__name__}: {error}", file=sys.stderr)
    print(f"Исполнено ноутбуков: {len(notebooks)}; ошибок: {failures}")
    return int(failures > 0)


if __name__ == "__main__":
    sys.exit(main())
