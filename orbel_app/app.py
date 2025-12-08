"""
Application bootstrap utilities.

This module centralises the QApplication initialisation and keeps GUI specific
setup out of any thin entry script so the rest of the package can be imported
in unit tests without side effects.
"""

from __future__ import annotations

from typing import Sequence, Tuple
import sys

from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from .ui.main_window import MainWindow


def create_application(argv: Sequence[str] | None = None) -> Tuple[QApplication, MainWindow]:
    """
    Configure and return the QApplication instance plus the main window.

    Keeping this logic in a helper makes it possible to unit test the window
    without spinning the Qt event loop.
    """

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setFont(QFont("Segoe UI", 11))

    window = MainWindow()
    window.showMaximized()
    return app, window


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by ``python -m orbel`` or ``orbel.main()``."""

    app, _window = create_application(argv)
    return app.exec_()