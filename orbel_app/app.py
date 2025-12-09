"""
Application bootstrap utilities.

This module centralises the QApplication initialisation and keeps GUI specific
setup out of any thin entry script so the rest of the package can be imported
in unit tests without side effects.
"""

from __future__ import annotations

from typing import Sequence, Tuple
import sys
import os

from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from .ui.main_window import MainWindow


def create_application(argv: Sequence[str] | None = None) -> Tuple[QApplication, MainWindow]:

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setFont(QFont("Segoe UI", 11))

    window = MainWindow()
    platform = (QApplication.platformName() or "").lower()
    xdg_session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    on_wayland = "wayland" in platform or xdg_session == "wayland"

    if on_wayland:
        screen = QApplication.primaryScreen()
        if screen is not None:
            avail = screen.availableGeometry()
            target_w = int(avail.width() * 0.9)
            target_h = int(avail.height() * 0.9)
            min_w = int(avail.width() * 0.8)
            min_h = int(avail.height() * 0.8)
            window.resize(target_w, target_h)
            window.setMinimumSize(min_w, min_h)
        window.showMaximized()
    else:
        window.showMaximized()
    return app, window


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by ``python -m orbel`` or ``orbel.main()``."""
    app, _window = create_application(argv)
    return app.exec_()