"""Core package for the orbel orbit visualisation application.

The main public entry point is exposed via :mod:`orbel`, which delegates to
the helpers in :mod:`orbel_app.app`. This keeps the Qt/bootstrap code in one
place while allowing the rest of the package to be imported in unit tests
without side effects.
"""

from .app import main  # Backwards-compatible import for existing callers.

__all__ = ["main"]
