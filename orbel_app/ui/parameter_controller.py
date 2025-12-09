"""Helpers for parameter control bindings."""

from __future__ import annotations

from functools import partial
from typing import Callable, Dict

from .panels import ParameterControl


class ParameterController:
    """Binds slider/spin controls and exposes typed get/set access for parameter values."""
    def __init__(self, controls: Dict[str, ParameterControl]) -> None:
        self.controls = controls

    def bind(self, key: str, callback: Callable[[], None]) -> None:
        ctrl = self.controls[key]
        ctrl.slider.valueChanged.connect(
            partial(self._sld_to_spn, spn=ctrl.spin, mn=ctrl.minimum, st=ctrl.step)
        )
        ctrl.spin.valueChanged.connect(
            partial(self._spn_to_sld, sld=ctrl.slider, mn=ctrl.minimum, st=ctrl.step)
        )
        ctrl.spin.valueChanged.connect(lambda _value, cb=callback: cb())

    @staticmethod
    def _sld_to_spn(v: int, *, spn, mn: float, st: float) -> None:
        spn.setValue(mn + v * st)

    @staticmethod
    def _spn_to_sld(x: float, *, sld, mn: float, st: float) -> None:
        sld.setValue(int(round((x - mn) / st)))

    def get_value(self, key: str) -> float:
        return float(self.controls[key].spin.value())

    def set_value(self, key: str, value: float) -> None:
        ctrl = self.controls[key]
        spn = ctrl.spin
        sld = ctrl.slider
        spn.blockSignals(True)
        sld.blockSignals(True)
        spn.setValue(value)
        sld.setValue(int(round((value - ctrl.minimum) / ctrl.step)))
        spn.blockSignals(False)
        sld.blockSignals(False)