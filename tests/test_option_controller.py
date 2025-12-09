"""Tests for the OptionController and its interaction with checkboxes."""

from __future__ import annotations

import pytest
from PyQt5.QtWidgets import QApplication, QCheckBox

from orbel_app.ui.option_controller import OptionController
from orbel_app.ui.panels import OptionSpec


@pytest.fixture(autouse=True)
def qapp():
    """Ensure a QApplication exists for these tests."""
    app = QApplication.instance() or QApplication([])
    yield app


class DummyAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bool]] = []

    def apply(self, key: str, value: bool) -> None:
        self.calls.append((key, bool(value)))


def _make_controller():
    specs = (
        OptionSpec("show_nodes", "Show nodes", checked=True),
        OptionSpec("show_bodies", "Show bodies", checked=False),
    )
    controller = OptionController(specs)
    return controller, specs


def test_attach_adapter_applies_initial_state_for_all_options():
    controller, specs = _make_controller()
    adapter = DummyAdapter()

    controller.attach_adapter(adapter)

    expected = {(spec.key, bool(spec.checked)) for spec in specs}
    assert set(adapter.calls) == expected


def test_register_checkboxes_initialises_state_and_toggles_propagate():
    controller, _ = _make_controller()

    cb_nodes = QCheckBox()
    cb_bodies = QCheckBox()
    controller.register_checkboxes(
        {"show_nodes": cb_nodes, "show_bodies": cb_bodies}
    )

    assert cb_nodes.isChecked() is True
    assert cb_bodies.isChecked() is False

    adapter = DummyAdapter()
    controller.attach_adapter(adapter)
    adapter.calls.clear()

    cb_bodies.setChecked(True)

    assert controller._state["show_bodies"].checked is True
    assert adapter.calls == [("show_bodies", True)]


def test_set_state_updates_internal_state_and_notifies_adapter():
    controller, _ = _make_controller()
    adapter = DummyAdapter()
    controller.attach_adapter(adapter)
    adapter.calls.clear()

    controller.set_state("show_nodes", False)

    assert controller._state["show_nodes"].checked is False
    assert adapter.calls == [("show_nodes", False)]

