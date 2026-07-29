#!/usr/bin/env python3
"""Быстрая статическая проверка Jupyter-ноутбуков без их исполнения."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

IGNORED_PARTS = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints"}
INSTALL_PATTERN = re.compile(r"(?:^|\n)\s*[!%]\s*pip\s+install\s+([^\n]+)", re.IGNORECASE)
ABSOLUTE_PATH_PATTERN = re.compile(
    r"""(?x)
    (?:["']/(?:Users|home)/[^"'\n]+)
    |
    (?:["'][A-Za-z]:\\\\[^"'\n]+)
    """
)
SECRET_PATTERN = re.compile(
    r"(?:gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})"
)


@dataclass(frozen=True, order=True)
class NotebookIssue:
    """Одна диагностическая запись валидатора."""

    path: Path
    level: str
    message: str


def discover_notebooks(paths: list[Path]) -> list[Path]:
    """Найти ноутбуки в переданных файлах и каталогах."""
    notebooks: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix == ".ipynb":
            notebooks.add(path)
        elif path.is_dir():
            notebooks.update(
                candidate
                for candidate in path.rglob("*.ipynb")
                if not IGNORED_PARTS.intersection(candidate.parts)
            )
    return sorted(notebooks)


def validate_notebook(path: Path, *, max_size_mb: float = 20.0) -> list[NotebookIssue]:
    """Проверить JSON-структуру, метаданные и отсутствие сохранённых результатов."""
    issues: list[NotebookIssue] = []
    if not path.exists():
        return [NotebookIssue(path, "ошибка", "файл не найден")]

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        issues.append(
            NotebookIssue(path, "ошибка", f"размер {size_mb:.1f} МБ превышает {max_size_mb:g} МБ")
        )

    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return [*issues, NotebookIssue(path, "ошибка", "файл должен быть в UTF-8")]
    except json.JSONDecodeError as error:
        return [
            *issues,
            NotebookIssue(path, "ошибка", f"некорректный JSON: строка {error.lineno}"),
        ]

    if not isinstance(notebook, dict):
        return [*issues, NotebookIssue(path, "ошибка", "корень JSON должен быть объектом")]
    if notebook.get("nbformat") != 4:
        issues.append(NotebookIssue(path, "ошибка", "поддерживается только nbformat 4"))

    cells = notebook.get("cells")
    if not isinstance(cells, list):
        return [*issues, NotebookIssue(path, "ошибка", "поле cells должно быть списком")]
    if not cells:
        issues.append(NotebookIssue(path, "предупреждение", "ноутбук не содержит ячеек"))

    metadata = notebook.get("metadata")
    if not isinstance(metadata, dict):
        issues.append(NotebookIssue(path, "ошибка", "поле metadata должно быть объектом"))
        metadata = {}
    kernelspec = metadata.get("kernelspec")
    if not isinstance(kernelspec, dict) or not kernelspec.get("name"):
        issues.append(NotebookIssue(path, "ошибка", "не указан metadata.kernelspec.name"))
    language = metadata.get("language_info")
    if not isinstance(language, dict) or not language.get("name"):
        issues.append(NotebookIssue(path, "ошибка", "не указан metadata.language_info.name"))

    course_ci = metadata.get("course_ci", {})
    if not isinstance(course_ci, dict):
        issues.append(NotebookIssue(path, "ошибка", "metadata.course_ci должен быть объектом"))
    elif "smoke" in course_ci and not isinstance(course_ci["smoke"], bool):
        issues.append(
            NotebookIssue(path, "ошибка", "metadata.course_ci.smoke должен быть true или false")
        )

    seen_cell_ids: set[str] = set()
    for index, cell in enumerate(cells, start=1):
        if not isinstance(cell, dict):
            issues.append(NotebookIssue(path, "ошибка", f"ячейка {index}: ожидается объект"))
            continue
        cell_id = cell.get("id")
        if not isinstance(cell_id, str) or not cell_id.strip():
            issues.append(NotebookIssue(path, "ошибка", f"ячейка {index}: отсутствует id"))
        elif cell_id in seen_cell_ids:
            issues.append(
                NotebookIssue(path, "ошибка", f"ячейка {index}: повторяющийся id {cell_id!r}")
            )
        else:
            seen_cell_ids.add(cell_id)
        cell_type = cell.get("cell_type")
        if cell_type not in {"code", "markdown", "raw"}:
            issues.append(
                NotebookIssue(path, "ошибка", f"ячейка {index}: неизвестный тип {cell_type!r}")
            )
            continue
        source = cell.get("source")
        if not isinstance(source, (str, list)):
            issues.append(
                NotebookIssue(
                    path, "ошибка", f"ячейка {index}: source должен быть строкой или списком"
                )
            )
            continue
        if cell_type != "code":
            continue

        if cell.get("outputs"):
            issues.append(NotebookIssue(path, "предупреждение", f"ячейка {index}: сохранён вывод"))
        if cell.get("execution_count") is not None:
            issues.append(
                NotebookIssue(path, "предупреждение", f"ячейка {index}: сохранён номер исполнения")
            )

        source_text = "".join(source) if isinstance(source, list) else source
        if ABSOLUTE_PATH_PATTERN.search(source_text):
            issues.append(
                NotebookIssue(path, "ошибка", f"ячейка {index}: найден абсолютный локальный путь")
            )
        if SECRET_PATTERN.search(source_text):
            issues.append(
                NotebookIssue(path, "ошибка", f"ячейка {index}: найден шаблон возможного секрета")
            )
        for match in INSTALL_PATTERN.finditer(source_text):
            requirements = match.group(1)
            if "==" not in requirements and " -r " not in f" {requirements} ":
                issues.append(
                    NotebookIssue(
                        path,
                        "предупреждение",
                        f"ячейка {index}: pip install без фиксации версии",
                    )
                )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Файлы или каталоги")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Считать предупреждения ошибками",
    )
    parser.add_argument(
        "--max-size-mb",
        type=float,
        default=20.0,
        help="Максимальный размер одного ноутбука (по умолчанию: 20)",
    )
    parser.add_argument("--quiet", action="store_true", help="Печатать только диагностику")
    args = parser.parse_args(argv)

    paths = args.paths or [Path.cwd()]
    notebooks = discover_notebooks(paths)
    issues = [
        issue
        for notebook in notebooks
        for issue in validate_notebook(notebook, max_size_mb=args.max_size_mb)
    ]
    for issue in sorted(issues):
        print(f"{issue.level.upper()}: {issue.path}: {issue.message}")

    errors = sum(issue.level == "ошибка" for issue in issues)
    warnings = sum(issue.level == "предупреждение" for issue in issues)
    if not args.quiet:
        print(
            f"Проверено ноутбуков: {len(notebooks)}; ошибок: {errors}; предупреждений: {warnings}"
        )
    return int(errors > 0 or (args.strict and warnings > 0))


if __name__ == "__main__":
    sys.exit(main())
