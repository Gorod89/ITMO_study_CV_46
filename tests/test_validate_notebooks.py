import json
import os
from pathlib import Path

from scripts import smoke_notebooks
from scripts.smoke_notebooks import is_marked_for_smoke, selected_notebooks
from scripts.validate_notebooks import validate_notebook


def write_notebook(path: Path, *, smoke: bool = False, output: bool = False) -> None:
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "id": "cell-001",
                "execution_count": 1 if output else None,
                "metadata": {},
                "outputs": [{"output_type": "stream", "name": "stdout", "text": "ok"}]
                if output
                else [],
                "source": ["print('ok')"],
            }
        ],
        "metadata": {
            "course_ci": {"smoke": smoke},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook), encoding="utf-8")


def test_valid_notebook_has_no_issues(tmp_path: Path) -> None:
    path = tmp_path / "valid.ipynb"
    write_notebook(path)
    assert validate_notebook(path) == []


def test_outputs_are_reported_as_warnings(tmp_path: Path) -> None:
    path = tmp_path / "output.ipynb"
    write_notebook(path, output=True)
    issues = validate_notebook(path)
    assert len(issues) == 2
    assert {issue.level for issue in issues} == {"предупреждение"}


def test_smoke_selection_requires_explicit_metadata(tmp_path: Path) -> None:
    marked = tmp_path / "marked.ipynb"
    regular = tmp_path / "regular.ipynb"
    write_notebook(marked, smoke=True)
    write_notebook(regular)

    assert is_marked_for_smoke(marked)
    assert selected_notebooks([], root=tmp_path) == [marked]
    assert selected_notebooks([regular], root=tmp_path) == [regular]


def test_smoke_cli_fails_when_nothing_is_selected(monkeypatch, capsys) -> None:
    monkeypatch.setattr(smoke_notebooks, "selected_notebooks", lambda paths: [])

    assert smoke_notebooks.main([]) == 2
    assert "не выбраны" in capsys.readouterr().err


def test_notebook_runtime_uses_temporary_writable_directories() -> None:
    before = {name: os.environ.get(name) for name in smoke_notebooks.ISOLATED_ENVIRONMENT_VARIABLES}

    with smoke_notebooks.isolated_notebook_environment() as root:
        for name in smoke_notebooks.ISOLATED_ENVIRONMENT_VARIABLES:
            configured = Path(os.environ[name])
            assert configured.is_dir()
            assert configured.is_relative_to(root)

    assert {
        name: os.environ.get(name) for name in smoke_notebooks.ISOLATED_ENVIRONMENT_VARIABLES
    } == before


def test_local_path_and_secret_are_errors(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.ipynb"
    write_notebook(path)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    notebook["cells"][0]["source"] = [
        'data = "/Users/student/private/data"\n',
        'token = "gho_abcdefghijklmnopqrstuvwxyz123456"\n',
    ]
    path.write_text(json.dumps(notebook), encoding="utf-8")

    issues = validate_notebook(path)
    assert len(issues) == 2
    assert {issue.level for issue in issues} == {"ошибка"}
