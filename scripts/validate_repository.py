#!/usr/bin/env python3
"""Проверка минимальных гарантий воспроизводимости репозитория."""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_notebooks import (  # noqa: E402
    IGNORED_PARTS,
    discover_notebooks,
    validate_notebook,
)

REQUIRED_FILES = (
    ".python-version",
    ".github/workflows/ci.yml",
    ".github/workflows/notebooks-smoke.yml",
    "Makefile",
    "pyproject.toml",
    "scripts/generate_smoke_data.py",
    "scripts/validate_markdown_links.py",
    "scripts/validate_notebooks.py",
)
FORBIDDEN_NAMES = {".DS_Store"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".ckpt", ".onnx", ".pt"}


@dataclass(frozen=True, order=True)
class RepositoryIssue:
    """Диагностика с уровнем серьёзности."""

    path: Path
    level: str
    message: str


def repository_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not IGNORED_PARTS.intersection(path.relative_to(root).parts)
    )


def validate_repository(root: Path) -> list[RepositoryIssue]:
    """Вернуть все обнаруженные проблемы, не изменяя репозиторий."""
    root = root.resolve()
    issues: list[RepositoryIssue] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(
                RepositoryIssue(Path(relative), "ошибка", "обязательный файл отсутствует")
            )

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            config = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
            issues.append(RepositoryIssue(pyproject, "ошибка", f"некорректный TOML: {error}"))
        else:
            python_range = config.get("project", {}).get("requires-python")
            if python_range != ">=3.11,<3.13":
                issues.append(
                    RepositoryIssue(
                        pyproject,
                        "ошибка",
                        "requires-python должен фиксировать поддерживаемые Python 3.11–3.12",
                    )
                )

    seen_casefold: dict[str, Path] = {}
    for path in repository_files(root):
        relative = path.relative_to(root)
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            issues.append(
                RepositoryIssue(relative, "ошибка", "сгенерированный артефакт попал в репозиторий")
            )
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 95:
            issues.append(
                RepositoryIssue(
                    relative, "ошибка", f"размер {size_mb:.1f} МБ превышает лимит 95 МБ"
                )
            )
        elif size_mb > 20 and path.suffix != ".pdf":
            issues.append(
                RepositoryIssue(
                    relative,
                    "предупреждение",
                    f"крупный файл ({size_mb:.1f} МБ): рассмотрите внешнее хранилище",
                )
            )

        key = relative.as_posix().casefold()
        previous = seen_casefold.get(key)
        if previous is not None and previous != relative:
            issues.append(
                RepositoryIssue(
                    relative,
                    "ошибка",
                    f"конфликт регистра имени с {previous.as_posix()}",
                )
            )
        seen_casefold[key] = relative

    for notebook in discover_notebooks([root]):
        relative = notebook.relative_to(root)
        for notebook_issue in validate_notebook(notebook):
            issues.append(RepositoryIssue(relative, notebook_issue.level, notebook_issue.message))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Корень репозитория")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Считать предупреждения ошибками",
    )
    args = parser.parse_args(argv)

    issues = validate_repository(args.root)
    for issue in sorted(issues):
        print(f"{issue.level.upper()}: {issue.path}: {issue.message}")
    errors = sum(issue.level == "ошибка" for issue in issues)
    warnings = sum(issue.level == "предупреждение" for issue in issues)
    print(f"Проверка репозитория завершена: ошибок {errors}, предупреждений {warnings}")
    return int(errors > 0 or (args.strict and warnings > 0))


if __name__ == "__main__":
    sys.exit(main())
