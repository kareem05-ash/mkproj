"""
Tests for mkproj.engine.

Verifies the filesystem engine in isolation using controlled
in-memory template trees.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mkproj.engine import EventKind, scaffold_project


@pytest.fixture()
def simple_template(tmp_path: Path) -> Path:
    """A minimal template with a directory, a text file, and a token file."""
    t = tmp_path / "template"
    (t / "src").mkdir(parents=True)
    (t / "src" / "main.c").write_text("// {{project_name}}", encoding="utf-8")
    (t / "README.md").write_text("# {{project_name}}", encoding="utf-8")
    (t / "Makefile").write_text("TARGET = {{project_name}}", encoding="utf-8")
    return t


class TestScaffoldProject:
    def test_destination_created(self, simple_template: Path, tmp_path: Path) -> None:
        dest = tmp_path / "out" / "myapp"
        list(scaffold_project(simple_template, dest, "myapp"))
        assert dest.is_dir()

    def test_token_replaced_in_file_content(
        self, simple_template: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "myapp"
        list(scaffold_project(simple_template, dest, "myapp"))
        readme = dest / "README.md"
        assert readme.read_text(encoding="utf-8") == "# myapp"

    def test_token_replaced_in_nested_file(
        self, simple_template: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "myapp"
        list(scaffold_project(simple_template, dest, "myapp"))
        main_c = dest / "src" / "main.c"
        assert "myapp" in main_c.read_text(encoding="utf-8")

    def test_dir_events_emitted(self, simple_template: Path, tmp_path: Path) -> None:
        dest = tmp_path / "myapp"
        events = list(scaffold_project(simple_template, dest, "myapp"))
        dir_events = [e for e in events if e.kind == EventKind.DIR_CREATED]
        assert any("src" in e.relative_path for e in dir_events)

    def test_file_events_emitted(self, simple_template: Path, tmp_path: Path) -> None:
        dest = tmp_path / "myapp"
        events = list(scaffold_project(simple_template, dest, "myapp"))
        file_events = [e for e in events if e.kind == EventKind.FILE_CREATED]
        assert len(file_events) >= 2

    def test_fails_if_destination_exists(
        self, simple_template: Path, tmp_path: Path
    ) -> None:
        dest = tmp_path / "myapp"
        dest.mkdir()
        with pytest.raises(FileExistsError):
            list(scaffold_project(simple_template, dest, "myapp"))
