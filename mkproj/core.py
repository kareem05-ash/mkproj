"""
Core orchestration for mkproj.

This module is the single entry point for creating a project.
It knows about validation, path resolution, and delegation to the
engine — but nothing about CLI presentation (no Rich, no Typer).

This makes it fully testable without mocking any output.

Public API:
    create_project(name, template, destination, config) -> ProjectResult
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from mkproj.config import Config
from mkproj.engine import ScaffoldEvent, scaffold_project
from mkproj.exceptions import (
    InvalidProjectNameError,
    ProjectExistsError,
    TemplateNotFoundError,
)

# Project names: lowercase/uppercase letters, digits, hyphens, underscores.
# Must start with a letter or digit (no leading dash).
_VALID_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]*$")
_MAX_NAME_LENGTH = 64


@dataclass
class ProjectResult:
    """
    Returned by :func:`create_project`.

    Always inspect ``success`` before using other fields.
    """

    success: bool
    project_path: Path | None
    template_used: str
    events: list[ScaffoldEvent] = field(default_factory=list)
    error: str | None = None

    def __bool__(self) -> bool:
        return self.success


def _validate_name(name: str) -> None:
    """
    Raise :class:`InvalidProjectNameError` if *name* is not acceptable.
    """
    if not name:
        raise InvalidProjectNameError(name, "project name cannot be empty")
    if len(name) > _MAX_NAME_LENGTH:
        raise InvalidProjectNameError(
            name,
            f"name exceeds maximum length of {_MAX_NAME_LENGTH} characters",
        )
    if not _VALID_NAME_RE.match(name):
        raise InvalidProjectNameError(
            name,
            "only letters, digits, hyphens, and underscores are allowed; "
            "name must start with a letter or digit",
        )


def _resolve_template(name: str, config: Config) -> Path:
    """
    Return the path to the requested template directory.

    Raises :class:`TemplateNotFoundError` if it cannot be found.
    """
    candidate = config.templates_dir / name
    if not candidate.is_dir():
        available = config.available_templates()
        hint = f"Available: {', '.join(available)}" if available else "No templates found."
        raise TemplateNotFoundError(name, str(config.templates_dir))
    return candidate


def create_project(
    name: str,
    template: str | None = None,
    destination: Path | None = None,
    config: Config | None = None,
) -> ProjectResult:
    """
    Scaffold a new project directory.

    Parameters
    ----------
    name:
        The project name. Used as the directory name and for
        ``{{project_name}}`` token replacement inside templates.
    template:
        Template name (e.g. ``"cpp"``).  Falls back to
        ``config.default_template`` when *None*.
    destination:
        Parent directory to create the project inside.
        Falls back to ``config.project_root`` when *None*.
    config:
        Runtime configuration.  Loaded from environment when *None*.

    Returns
    -------
    ProjectResult
        Always returned; never raises.  Inspect ``.success``.
    """
    cfg = config or Config.load()
    resolved_template = template or cfg.default_template
    resolved_parent = destination or cfg.project_root

    try:
        _validate_name(name)
        template_path = _resolve_template(resolved_template, cfg)

        project_path = resolved_parent / name
        if project_path.exists():
            raise ProjectExistsError(str(project_path))

        events = list(
            scaffold_project(
                source=template_path,
                destination=project_path,
                project_name=name,
            )
        )

        return ProjectResult(
            success=True,
            project_path=project_path,
            template_used=resolved_template,
            events=events,
        )

    except (InvalidProjectNameError, TemplateNotFoundError, ProjectExistsError) as exc:
        return ProjectResult(
            success=False,
            project_path=None,
            template_used=resolved_template,
            error=str(exc),
        )
    except OSError as exc:
        return ProjectResult(
            success=False,
            project_path=None,
            template_used=resolved_template,
            error=f"Filesystem error: {exc}",
        )
