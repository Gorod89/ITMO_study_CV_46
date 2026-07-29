from pathlib import Path

from scripts.validate_repository import REQUIRED_FILES, validate_repository


def test_missing_required_files_are_reported(tmp_path: Path) -> None:
    issues = validate_repository(tmp_path)
    missing = {issue.path.as_posix() for issue in issues if issue.level == "ошибка"}
    assert set(REQUIRED_FILES).issubset(missing)


def test_python_range_is_checked(tmp_path: Path) -> None:
    for relative in REQUIRED_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nrequires-python = ">=3.10"\n',
        encoding="utf-8",
    )

    issues = validate_repository(tmp_path)
    assert any("Python 3.11–3.12" in issue.message for issue in issues)
