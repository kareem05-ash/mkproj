"""
Configuration management for mkproj.

Currently resolves from environment variables and built-in defaults.
The architecture is intentionally prepared for TOML config file support
(e.g. ~/.config/mkproj/config.toml) without requiring changes to any
other module — only this file would grow.

Usage:
    config = Config.load()
    print(config.default_template)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


# The templates/ directory ships alongside the package.
# We resolve it relative to this file at import time.
_PACKAGE_ROOT = Path(__file__).parent.parent
_BUNDLED_TEMPLATES_DIR = _PACKAGE_ROOT / "templates"


@dataclass(frozen=True)
class Config:
    """Resolved runtime configuration."""

    default_template: str
    """Template name used when --template is not supplied."""

    project_root: Path
    """Parent directory where new projects are created."""

    templates_dir: Path
    """Directory that contains template sub-folders."""

    @classmethod
    def load(cls) -> "Config":
        """
        Build a Config from the environment (and later, a TOML file).

        Resolution order (highest priority first):
          1. Environment variables  MKPROJ_DEFAULT_TEMPLATE, MKPROJ_ROOT
          2. Hardcoded defaults

        Future: insert TOML file reading between steps 1 and 2.
        """
        default_template = os.environ.get("MKPROJ_DEFAULT_TEMPLATE", "cpp")
        project_root_raw = os.environ.get("MKPROJ_ROOT", "")
        project_root = (
            Path(project_root_raw).expanduser().resolve()
            if project_root_raw
            else Path.cwd()
        )

        return cls(
            default_template=default_template,
            project_root=project_root,
            templates_dir=_BUNDLED_TEMPLATES_DIR,
        )

    def available_templates(self) -> list[str]:
        """Return the names of all templates found in templates_dir."""
        if not self.templates_dir.exists():
            return []
        return sorted(
            p.name for p in self.templates_dir.iterdir() if p.is_dir()
        )
