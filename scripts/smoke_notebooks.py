#!/usr/bin/env python3
"""Исполнить только явно помеченные smoke-ноутбуки без сохранения результата."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import socket
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_notebooks import discover_notebooks  # noqa: E402

ISOLATED_ENVIRONMENT_VARIABLES = (
    "IPYTHONDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_DATA_DIR",
    "JUPYTER_RUNTIME_DIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
)


@contextlib.contextmanager
def isolated_notebook_environment() -> Iterator[Path]:
    """Перенаправить служебные записи Jupyter/IPython во временный каталог."""
    previous = {name: os.environ.get(name) for name in ISOLATED_ENVIRONMENT_VARIABLES}
    with tempfile.TemporaryDirectory(prefix="cv-course-jupyter-") as directory:
        root = Path(directory)
        for name in ISOLATED_ENVIRONMENT_VARIABLES:
            path = root / name.lower()
            path.mkdir()
            os.environ[name] = str(path)
        try:
            yield root
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


def local_kernel_transport_available() -> bool:
    """Проверить, разрешает ли среда открыть loopback-порт для Jupyter kernel."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", 0))
        except PermissionError:
            return False
    return True


def execute_cells_in_process(notebook, path: Path) -> None:
    """Последовательно исполнить plain-Python ячейки доверенного smoke-ноутбука."""
    namespace = {"__name__": "__main__"}
    previous_directory = Path.cwd()
    try:
        os.chdir(path.parent)
        for index, cell in enumerate(notebook.cells, start=1):
            if cell.cell_type != "code":
                continue
            source = str(cell.source)
            if source.lstrip().startswith(("%", "!")):
                raise RuntimeError(
                    f"ячейка {index} содержит Jupyter magic, недоступный in-process executor"
                )
            exec(compile(source, f"{path}:ячейка-{index}", "exec"), namespace, namespace)
    finally:
        os.chdir(previous_directory)


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
        from jupyter_client import AsyncKernelManager
        from nbclient import NotebookClient
    except ImportError as error:
        raise RuntimeError(
            "Установите группу notebooks: uv sync --group notebooks --extra cv"
        ) from error

    with isolated_notebook_environment() as runtime_root:
        notebook = nbformat.read(path, as_version=4)
        kernel_name = notebook.metadata.get("kernelspec", {}).get("name", "python3")
        if not local_kernel_transport_available():
            if not is_marked_for_smoke(path):
                raise RuntimeError(
                    "Среда запрещает Jupyter kernel transport; in-process fallback "
                    "разрешён только для metadata.course_ci.smoke=true"
                )
            print(f"ОГРАНИЧЕННАЯ СРЕДА: in-process smoke executor для {path}")
            execute_cells_in_process(notebook, path)
            return
        kernel_manager = None
        if os.name != "nt":
            kernel_manager = AsyncKernelManager(
                kernel_name=kernel_name,
                transport="ipc",
                ip=str(runtime_root / "kernel"),
            )
        client = NotebookClient(
            notebook,
            timeout=timeout,
            kernel_name=kernel_name,
            km=kernel_manager,
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
            "ОШИБКА: smoke-ноутбуки не выбраны. Передайте путь явно или добавьте "
            "metadata.course_ci.smoke=true.",
            file=sys.stderr,
        )
        return 2

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
