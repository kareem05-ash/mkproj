"""
Tests for mkproj.core.

These tests run without touching the real filesystem (via tmp_path)
and without any CLI or output coupling.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from mkproj.config import Config
from mkproj.core import create_project


# ---------------------------------------------------------------------------
# Fixture: isolated config pointing at our real templates/
# ---------------------------------------------------------------------------

@pytest.fixture()
def config(tmp_path: Path) -> Config:
    """Config rooted at a temp directory, using the real bundled templates."""
    from mkproj.config import _BUNDLED_TEMPLATES_DIR  # noqa: PLC0415

    return Config(
        default_template="cpp",
        project_root=tmp_path,
        templates_dir=_BUNDLED_TEMPLATES_DIR,
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestCreateProject:
    def test_creates_project_directory(self, config: Config, tmp_path: Path) -> None:
        result = create_project("myapp", config=config)
        assert result.success
        assert result.project_path is not None
        assert result.project_path.is_dir()

    def test_uses_default_template(self, config: Config) -> None:
        result = create_project("myapp", config=config)
        assert result.template_used == "cpp"

    def test_explicit_template_selection(self, config: Config) -> None:
        result = create_project("myapp", template="python", config=config)
        assert result.success
        assert result.template_used == "python"

    def test_events_emitted(self, config: Config) -> None:
        result = create_project("myapp", config=config)
        assert result.events, "Expected at least one scaffold event"

    def test_token_replacement_in_readme(self, config: Config) -> None:
        result = create_project("coolproject", config=config)
        assert result.project_path is not None
        readme = result.project_path / "README.md"
        assert readme.exists()
        content = readme.read_text(encoding="utf-8")
        assert "coolproject" in content
        assert "{{project_name}}" not in content

    def test_custom_destination(self, config: Config, tmp_path: Path) -> None:
        custom = tmp_path / "workspace"
        custom.mkdir()
        config2 = Config(
            default_template=config.default_template,
            project_root=custom,
            templates_dir=config.templates_dir,
        )
        result = create_project("proj", config=config2)
        assert result.success
        assert result.project_path == custom / "proj"


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------

class TestValidation:
    def test_empty_name_fails(self, config: Config) -> None:
        result = create_project("", config=config)
        assert not result.success
        assert result.error is not None

    def test_name_with_space_fails(self, config: Config) -> None:
        result = create_project("my project", config=config)
        assert not result.success

    def test_name_leading_dash_fails(self, config: Config) -> None:
        result = create_project("-badname", config=config)
        assert not result.success

    def test_name_too_long_fails(self, config: Config) -> None:
        result = create_project("a" * 65, config=config)
        assert not result.success

    def test_duplicate_project_fails(self, config: Config) -> None:
        create_project("myapp", config=config)
        result = create_project("myapp", config=config)
        assert not result.success
        assert result.error is not None
        assert "already exists" in result.error

    def test_unknown_template_fails(self, config: Config) -> None:
        result = create_project("myapp", template="nonexistent", config=config)
        assert not result.success
        assert result.error is not None
