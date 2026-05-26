"""
Domain exceptions for mkproj.

Keeping exceptions typed and separate from logic lets callers
(cli.py, tests) handle failure cases explicitly without catching
broad Exception types.
"""


class MkprojError(Exception):
    """Base class for all mkproj errors."""


class ProjectExistsError(MkprojError):
    """Raised when the target project directory already exists."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Project directory already exists: {path}")


class TemplateNotFoundError(MkprojError):
    """Raised when the requested template cannot be located."""

    def __init__(self, name: str, search_path: str) -> None:
        self.name = name
        self.search_path = search_path
        super().__init__(
            f"Template '{name}' not found in: {search_path}"
        )


class InvalidProjectNameError(MkprojError):
    """Raised when the project name fails validation."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason
        super().__init__(f"Invalid project name '{name}': {reason}")
