"""
Command-line interface for mkproj.

This module owns:
  - Argument/option parsing (via Typer)
  - Rich terminal output (success tree, error messages)
  - Exit codes

It does NOT own any scaffolding logic. All work is delegated to
``mkproj.core.create_project()``.

CLI design
----------
Two entry points are registered in pyproject.toml:

    mkproj <name> [--template T] [--dest D]   → scaffold a project
    mkproj-templates                           → list available templates

This gives the user the clean `mkproj myapp` UX without fighting Typer's
subcommand routing, while keeping the templates listing as a separate
first-class command.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from mkproj.config import Config
from mkproj.core import ProjectResult, create_project
from mkproj.engine import EventKind

# Two separate single-command apps — clean, no subcommand routing friction.
app = typer.Typer(
    name="mkproj",
    help="Scaffold a new project from a template.",
    add_completion=False,
    rich_markup_mode="rich",
)

templates_app = typer.Typer(
    name="mkproj-templates",
    help="List available mkproj templates.",
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_result(result: ProjectResult) -> None:
    """Render a rich summary of the scaffold result."""
    tree = Tree(
        f"[bold cyan]{result.project_path.name if result.project_path else '?'}[/]",
        guide_style="dim",
    )

    for event in result.events:
        if event.kind == EventKind.DIR_CREATED:
            tree.add(f"[blue]{event.relative_path}/[/]")
        elif event.kind == EventKind.FILE_CREATED:
            tree.add(f"[green]{event.relative_path}[/]")

    console.print()
    console.print(tree)
    console.print()
    console.print(
        Panel(
            Text.assemble(
                ("✓ ", "bold green"),
                ("Project created successfully\n", "bold white"),
                ("  Template : ", "dim"),
                (result.template_used, "cyan"),
                "\n",
                ("  Location : ", "dim"),
                (str(result.project_path), "cyan"),
            ),
            border_style="green",
            expand=False,
        )
    )
    console.print()
    console.print(f"[dim]  cd [bold]{result.project_path}[/bold][/dim]\n")


def _print_error(message: str) -> None:
    err_console.print(
        Panel(
            Text.assemble(("✗ ", "bold red"), (message, "white")),
            border_style="red",
            expand=False,
        )
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def create(
    name: Annotated[
        str,
        typer.Argument(help="Project name (used as the directory name)."),
    ],
    template: Annotated[
        Optional[str],
        typer.Option(
            "--template", "-t",
            help="Template to use (e.g. cpp, python). Run mkproj-templates to list.",
        ),
    ] = None,
    dest: Annotated[
        Optional[Path],
        typer.Option(
            "--dest", "-d",
            help="Parent directory to create the project in. Defaults to CWD.",
        ),
    ] = None,
) -> None:
    """
    Scaffold a new [bold cyan]NAME[/bold cyan] project from a template.

    Examples:

      mkproj myapp
      mkproj myapp --template python
      mkproj myapp --template cpp --dest ~/projects
    """
    config = Config.load()
    result = create_project(name=name, template=template, destination=dest, config=config)

    if result:
        _print_result(result)
        raise typer.Exit(0)
    else:
        _print_error(result.error or "Unknown error.")
        raise typer.Exit(1)


@templates_app.command()
def list_templates() -> None:
    """List all available project templates."""
    config = Config.load()
    available = config.available_templates()

    if not available:
        console.print("[yellow]No templates found.[/yellow]")
        return

    console.print("\n[bold]Available templates:[/bold]")
    for name in available:
        marker = "[green]●[/green]" if name == config.default_template else " "
        console.print(f"  {marker} {name}")
    console.print(
        f"\n[dim]Default: [cyan]{config.default_template}[/cyan] "
        f"(override with MKPROJ_DEFAULT_TEMPLATE)[/dim]\n"
    )


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def main() -> None:  # pragma: no cover
    app()


def main_templates() -> None:  # pragma: no cover
    templates_app()


if __name__ == "__main__":  # pragma: no cover
    main()
