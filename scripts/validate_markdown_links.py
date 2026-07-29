#!/usr/bin/env python3
"""Проверить, что локальные ссылки из Markdown ведут на существующие файлы."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

IGNORED_PARTS = {".git", ".venv", "venv", "__pycache__"}
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


def markdown_files(paths: list[Path]) -> list[Path]:
    """Найти Markdown-файлы, исключив служебные окружения."""
    result: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            result.add(path)
        elif path.is_dir():
            result.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and candidate.suffix.lower() in {".md", ".markdown"}
                and not IGNORED_PARTS.intersection(candidate.parts)
            )
    return sorted(result)


def broken_links(path: Path) -> list[tuple[int, str]]:
    """Вернуть номера строк и отсутствующие локальные цели."""
    failures: list[tuple[int, str]] = []
    text = path.read_text(encoding="utf-8")
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for raw_target in LINK_PATTERN.findall(line):
            target = raw_target.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme.lower() in EXTERNAL_SCHEMES or target.startswith("#"):
                continue
            if parsed.scheme or not parsed.path or "{" in parsed.path:
                continue
            local = (path.parent / unquote(parsed.path)).resolve()
            if not local.exists():
                failures.append((line_number, target))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Файлы или каталоги")
    args = parser.parse_args(argv)

    files = markdown_files(args.paths or [Path.cwd()])
    failures = [(path, line, target) for path in files for line, target in broken_links(path)]
    for path, line, target in failures:
        print(f"ОШИБКА: {path}:{line}: локальная ссылка не найдена: {target}")
    print(f"Проверено Markdown-файлов: {len(files)}; битых локальных ссылок: {len(failures)}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
