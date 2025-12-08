"""Tests for the ParameterController helper."""

from __future__ import annotations

import pytest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QSlider

from orbel_app.ui.panels import ParameterControl
from orbel_app.ui.parameter_controller import ParameterController


@pytest.fixture(autouse=True)
def qapp():
    """Ensure a QApplication exists for all tests in this module."""
    app = QApplication.instance() or QApplication([])
    yield app


def _make_controller(minimum: float = 0.0, step: float = 1.0):
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(100)

    spin = QDoubleSpinBox()
    spin.setRange(-1e6, 1e6)

    ctrl = ParameterControl(slider=slider, spin=spin, minimum=minimum, step=step)
    controller = ParameterController({"p": ctrl})
    return controller, slider, spin


def test_bind_keeps_slider_and_spin_in_sync():
    controller, slider, spin = _make_controller(minimum=1.0, step=0.5)

    calls: list[float] = []
    controller.bind("p", lambda: calls.append(controller.get_value("p")))

    slider.setValue(2)
    assert spin.value() == pytest.approx(1.0 + 2 * 0.5)
    assert calls[-1] == pytest.approx(controller.get_value("p"))

    calls.clear()
    spin.setValue(3.0)
    expected_slider = int(round((3.0 - 1.0) / 0.5))
    assert slider.value() == expected_slider
    assert calls[-1] == pytest.approx(controller.get_value("p"))


def test_set_value_updates_widgets_without_triggering_callbacks():
    controller, slider, spin = _make_controller(minimum=0.0, step=1.0)

    call_count = {"n": 0}

    def _cb():
        call_count["n"] += 1

    controller.bind("p", _cb)
    call_count["n"] = 0

    controller.set_value("p", 5.0)

    assert controller.get_value("p") == pytest.approx(5.0)
    assert spin.value() == pytest.approx(5.0)
    assert slider.value() == 5
    assert call_count["n"] == 0

