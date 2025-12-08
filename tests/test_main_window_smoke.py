"""Smoke tests for constructing and interacting with the main Qt window."""

from __future__ import annotations

import matplotlib
import pytest
from PyQt5.QtWidgets import QApplication

from orbel_app.ui.main_window import MainWindow


matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def qapp():
    """Ensure a QApplication exists for these tests."""
    app = QApplication.instance() or QApplication([])
    yield app


def test_main_window_constructs_and_initialises_without_crash():
    window = MainWindow()

    assert window.windowTitle() == "orbel"
    assert window.param_ctrl is not None
    assert window.canvas_manager is not None

    window.apply_params_from_init()
    window.reset_view()


def test_main_window_toggle_option_triggers_canvas_update(monkeypatch):
    window = MainWindow()

    calls = []

    class DummyAdapter:
        def apply(self, key, value):
            calls.append((key, bool(value)))

    window.option_controller.attach_adapter(DummyAdapter())  # type: ignore[arg-type]

    window.option_controller.set_state("show_nodes", False)

    assert ("show_nodes", False) in calls
