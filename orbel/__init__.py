"""Top-level package for the orbel orbit visualisation application.

This package exposes :func:`orbel.main` as the public entry point so the
application can be started with ``python -m orbel`` or imported from Python
code as ``import orbel``.
"""

from orbel_app.app import main, create_application

__all__ = ["main", "create_application"]

