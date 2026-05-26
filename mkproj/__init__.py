"""
mkproj — Professional project scaffolding CLI.

Public API surface (importable as a library):
    from mkproj import create_project, ProjectResult
"""

from mkproj.core import ProjectResult, create_project

__all__ = ["create_project", "ProjectResult"]
__version__ = "0.1.0"
