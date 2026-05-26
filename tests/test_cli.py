"""
CLI smoke tests for mkproj.

Uses Typer's built-in CliRunner so we test the full command surface
without spawning subprocesses.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mkproj.cli import app, templates_app

runner = CliRunner()


class TestCLICreate:
    def test_basic_invocation_exits_zero(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["myapp", "--dest", str(tmp_path)])
        assert result.exit_code == 0, result.output

    def test_output_contains_success_marker(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["myapp", "--dest", str(tmp_path)])
        assert "created successfully" in result.output.lower() or "✓" in result.output

    def test_project_directory_created(self, tmp_path: Path) -> None:
        runner.invoke(app, ["myapp", "--dest", str(tmp_path)])
        assert (tmp_path / "myapp").is_dir()

    def test_unknown_template_exits_nonzero(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app, ["myapp", "--template", "doesnotexist", "--dest", str(tmp_path)]
        )
        assert result.exit_code != 0

    def test_duplicate_project_exits_nonzero(self, tmp_path: Path) -> None:
        runner.invoke(app, ["myapp", "--dest", str(tmp_path)])
        result = runner.invoke(app, ["myapp", "--dest", str(tmp_path)])
        assert result.exit_code != 0

    def test_template_flag_respected(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app, ["myapp", "--template", "python", "--dest", str(tmp_path)]
        )
        assert result.exit_code == 0, result.output


class TestCLITemplates:
    def test_templates_command_exits_zero(self) -> None:
        result = runner.invoke(templates_app, [])
        assert result.exit_code == 0

    def test_templates_command_lists_cpp(self) -> None:
        result = runner.invoke(templates_app, [])
        assert "cpp" in result.output
