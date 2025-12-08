"""Helpers for locating and loading Qt icon resources from the icons/ directory."""

from pathlib import Path
from PyQt5.QtGui import QIcon

_ROOT = Path(__file__).resolve().parents[2]
_ICON_DIR = _ROOT / "icons"

def load_icon(name: str) -> QIcon:
    """Return a QIcon loaded from the project icon directory."""
    return QIcon(str(_ICON_DIR / name))