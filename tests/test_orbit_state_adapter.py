"""Tests for the OrbitStateAdapter mapping between UI controls and models."""

from __future__ import annotations

import numpy as np

from orbel_app.plotting.models import MassParameters, OrbitParameters
from orbel_app.ui.orbit_state import OrbitStateAdapter


class FakeParameterController:
    """Minimal stand-in for ParameterController used by OrbitStateAdapter tests."""

    def __init__(self, initial: dict[str, float] | None = None) -> None:
        self.values: dict[str, float] = dict(initial or {})
        self.set_calls: list[tuple[str, float]] = []

    def get_value(self, key: str) -> float:
        return float(self.values[key])

    def set_value(self, key: str, value: float) -> None:
        self.values[key] = float(value)
        self.set_calls.append((key, float(value)))


def test_read_orbit_params_converts_degrees_to_radians():
    ctrl = FakeParameterController(
        {
            "a": 2.0,
            "e": 0.3,
            "i": 45.0,
            "w": 30.0,
            "Om": 60.0,
        }
    )
    adapter = OrbitStateAdapter(ctrl)  # type: ignore[arg-type]

    params = adapter.read_orbit_params(start_nu=1.23)

    assert params.a == 2.0
    assert params.e == 0.3
    assert params.i == np.deg2rad(45.0)
    assert params.w == np.deg2rad(30.0)
    assert params.Om == np.deg2rad(60.0)
    assert params.start_nu == 1.23


def test_write_orbit_params_converts_radians_to_degrees():
    ctrl = FakeParameterController()
    adapter = OrbitStateAdapter(ctrl)  # type: ignore[arg-type]

    params = OrbitParameters(
        a=1.5,
        e=0.1,
        i=np.pi / 4,
        w=np.pi / 6,
        Om=np.pi / 3,
        start_nu=0.0,
    )

    adapter.write_orbit_params(params)

    assert ctrl.values["a"] == 1.5
    assert ctrl.values["e"] == 0.1
    assert ctrl.values["i"] == np.rad2deg(np.pi / 4)
    assert ctrl.values["w"] == np.rad2deg(np.pi / 6)
    assert ctrl.values["Om"] == np.rad2deg(np.pi / 3)


def test_read_and_write_masses_round_trip():
    ctrl = FakeParameterController({"m1": 2.0, "m2": 1.0})
    adapter = OrbitStateAdapter(ctrl)  # type: ignore[arg-type]

    masses = adapter.read_masses()
    assert isinstance(masses, MassParameters)
    assert masses.m1 == 2.0
    assert masses.m2 == 1.0

    new_masses = MassParameters(m1=3.5, m2=0.7)
    adapter.write_masses(new_masses)

    assert ctrl.values["m1"] == 3.5
    assert ctrl.values["m2"] == 0.7

