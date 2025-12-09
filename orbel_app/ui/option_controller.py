"""Centralized option state + toggle dispatching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from PyQt5.QtWidgets import QCheckBox

from .panels import OptionSpec
from .toggle_adapter import ToggleAdapter


@dataclass(slots=True)
class OptionState:
    """Simple container for checkbox state used by OptionController."""
    checked: bool


class OptionController:
    """Tracks option checkbox state and forwards visibility changes through a toggle adapter."""
    def __init__(self, specs: Iterable[OptionSpec]) -> None:
        self._state: Dict[str, OptionState] = {
            spec.key: OptionState(bool(spec.checked)) for spec in specs
        }
        self._checkboxes: Dict[str, QCheckBox] = {}
        self._adapter: ToggleAdapter | None = None

    def attach_adapter(self, adapter: ToggleAdapter | None) -> None:
        self._adapter = adapter
        self.apply_all()

    def register_checkboxes(self, mapping: Dict[str, QCheckBox]) -> None:
        for key, checkbox in mapping.items():
            self._checkboxes[key] = checkbox
            checkbox.blockSignals(True)
            checkbox.setChecked(self._state.get(key, OptionState(True)).checked)
            checkbox.blockSignals(False)
            checkbox.toggled.connect(lambda checked, k=key: self.set_state(k, checked))

    def set_state(self, key: str, value: bool) -> None:
        self._state.setdefault(key, OptionState(True)).checked = bool(value)
        self._apply_toggle(key)

    def apply_all(self) -> None:
        for key in self._state.keys():
            self._apply_toggle(key)

    def _apply_toggle(self, key: str) -> None:
        adapter = self._adapter
        if adapter is None:
            return
        adapter.apply(key, self._state[key].checked)