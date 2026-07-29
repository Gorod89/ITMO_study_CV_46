from pathlib import Path

from scripts.validate_markdown_links import broken_links, markdown_files


def test_local_links_and_code_fences(tmp_path: Path) -> None:
    existing = tmp_path / "файл с пробелом.md"
    existing.write_text("# Раздел\n", encoding="utf-8")
    document = tmp_path / "README.md"
    document.write_text(
        "\n".join(
            [
                "[Есть](%D1%84%D0%B0%D0%B9%D0%BB%20%D1%81%20%D0%BF%D1%80%D0%BE%D0%B1%D0%B5%D0%BB%D0%BE%D0%BC.md)",
                "[Внешняя](https://example.org/no-check)",
                "[Якорь](#раздел)",
                "```markdown",
                "[Пример](missing-in-code.md)",
                "```",
                "[Нет](missing.md)",
            ]
        ),
        encoding="utf-8",
    )

    assert broken_links(document) == [(7, "missing.md")]


def test_markdown_discovery_ignores_virtual_environment(tmp_path: Path) -> None:
    visible = tmp_path / "README.md"
    hidden = tmp_path / ".venv" / "PACKAGE.md"
    hidden.parent.mkdir()
    visible.write_text("", encoding="utf-8")
    hidden.write_text("", encoding="utf-8")

    assert markdown_files([tmp_path]) == [visible]
