"""
Filesystem engine for mkproj.

This module is responsible for the *physical* work: copying template
trees, creating directories, and rendering file content.

Design rules:
- No CLI knowledge (no Rich, no Typer).
- No Config knowledge — receives fully-resolved Path objects.
- Yields ScaffoldEvent objects so callers can report progress
  however they like (rich output, tests, future logging).
- Handles {{project_name}} token replacement in file content.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Generator


class EventKind(Enum):
    DIR_CREATED = auto()
    FILE_CREATED = auto()
    FILE_SKIPPED = auto()  # binary files, etc.


@dataclass(frozen=True)
class ScaffoldEvent:
    """Emitted for each item processed during scaffolding."""

    kind: EventKind
    relative_path: str  # e.g. "src/main.cpp"


# Token pattern: {{project_name}} in template files.
_TOKEN_RE = re.compile(r"\{\{project_name\}\}")

# File extensions considered safe to read/write as UTF-8 text.
_TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".c", ".cpp", ".h", ".hpp", ".cc",
        ".py", ".pyi",
        ".md", ".txt", ".rst",
        ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg",
        ".gitignore", ".env", ".env.example",
        ".html", ".css", ".js", ".ts", ".jsx", ".tsx",
        ".sh", ".bash", ".zsh",
        "Makefile", "Dockerfile",
    }
)


def _is_text_file(path: Path) -> bool:
    """Return True if the file should be treated as text (UTF-8)."""
    # Match by suffix first; also match suffix-less filenames like 'Makefile'.
    return path.suffix in _TEXT_EXTENSIONS or path.name in _TEXT_EXTENSIONS


def scaffold_project(
    source: Path,
    destination: Path,
    project_name: str,
) -> Generator[ScaffoldEvent, None, None]:
    """
    Copy *source* template tree into *destination*, replacing
    ``{{project_name}}`` tokens in both file names and text content.

    Yields a :class:`ScaffoldEvent` for every directory or file processed.

    Parameters
    ----------
    source:
        The template directory to copy from (must exist).
    destination:
        The target project directory to create (must NOT exist).
    project_name:
        Used to replace ``{{project_name}}`` tokens.
    """
    destination.mkdir(parents=True, exist_ok=False)

    for src_item in _walk_template(source):
        rel = src_item.relative_to(source)

        # Replace {{project_name}} tokens in path components.
        rendered_parts = [_TOKEN_RE.sub(project_name, p) for p in rel.parts]
        dst_item = destination.joinpath(*rendered_parts)

        if src_item.is_dir():
            dst_item.mkdir(parents=True, exist_ok=True)
            yield ScaffoldEvent(EventKind.DIR_CREATED, str(Path(*rendered_parts)))

        elif src_item.is_file():
            dst_item.parent.mkdir(parents=True, exist_ok=True)
            if _is_text_file(src_item):
                _copy_text_file(src_item, dst_item, project_name)
            else:
                shutil.copy2(src_item, dst_item)
            yield ScaffoldEvent(EventKind.FILE_CREATED, str(Path(*rendered_parts)))


def _walk_template(root: Path) -> Generator[Path, None, None]:
    """
    Yield every item in *root* (dirs first, then files) in a
    deterministic, sorted order.
    """
    items = sorted(root.rglob("*"), key=lambda p: (p.is_file(), str(p)))
    yield from items


def _copy_text_file(src: Path, dst: Path, project_name: str) -> None:
    """Read *src* as UTF-8, replace tokens, write to *dst*."""
    try:
        content = src.read_text(encoding="utf-8")
        rendered = _TOKEN_RE.sub(project_name, content)
        dst.write_text(rendered, encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback: treat as binary if UTF-8 decode fails.
        shutil.copy2(src, dst)
