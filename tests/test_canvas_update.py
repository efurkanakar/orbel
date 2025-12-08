"""Smoke tests for the PyQt/Matplotlib canvas integration."""

import matplotlib
import pytest

# Force a headless backend so the test suite can run without a display server.
matplotlib.use("Agg")

try:  # pragma: no cover - optional dependency
    import pytestqt  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytestqt = None

if pytestqt is None:
    from PyQt5.QtWidgets import QApplication

    @pytest.fixture
    def qtbot():
        app = QApplication.instance() or QApplication([])

        class _DummyQtBot:
            def __init__(self, app):
                self.app = app

            def addWidget(self, widget):
                widget.setParent(None)
                return widget

        yield _DummyQtBot(app)

from orbel_app.plotting.relative_canvas import RelativeCanvas
from orbel_app.plotting.absolute_canvas import AbsoluteCanvas


def test_relative_canvas_update_all(qtbot):
    canvas = RelativeCanvas()
    # Register the widgets with qtbot to ensure proper cleanup.
    qtbot.addWidget(canvas.card3d)
    qtbot.addWidget(canvas.card2d)

    # update_all should not raise even in headless mode.
    canvas.update_all()
    canvas.stop()


def test_absolute_canvas_update_all(qtbot):
    canvas = AbsoluteCanvas()
    qtbot.addWidget(canvas.card3d)
    qtbot.addWidget(canvas.card2d)

    canvas.update_all()
    canvas.stop()
