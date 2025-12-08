"""Bridge between option controller and canvas manager visibility API."""

from __future__ import annotations

from .canvas_manager import CanvasManager


class ToggleAdapter:
    """Thin wrapper that forwards toggle changes to CanvasManager."""

    def __init__(self, manager: CanvasManager) -> None:
        self._manager = manager

    def apply(self, key: str, value: bool) -> None:
        self._manager.set_visibility(key, value)