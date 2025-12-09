"""Helpers that map UI control values to orbit model structures."""

from __future__ import annotations

import numpy as np

from ..plotting.models import OrbitParameters, MassParameters
from .parameter_controller import ParameterController


class OrbitStateAdapter:
    """Read/write orbital parameters from the shared parameter controls."""

    def __init__(self, controls: ParameterController) -> None:
        self.controls = controls

    def read_orbit_params(self, *, start_nu: float) -> OrbitParameters:

        return OrbitParameters(a=self.controls.get_value("a"),
                               e=self.controls.get_value("e"),
                               i=np.deg2rad(self.controls.get_value("i")),
                               w=np.deg2rad(self.controls.get_value("w")),
                               Om=np.deg2rad(self.controls.get_value("Om")),
                               start_nu=float(start_nu))

    def write_orbit_params(self, params: OrbitParameters) -> None:
        self.controls.set_value("a", params.a)
        self.controls.set_value("e", params.e)
        self.controls.set_value("i", np.rad2deg(params.i))
        self.controls.set_value("w", np.rad2deg(params.w))
        self.controls.set_value("Om", np.rad2deg(params.Om))

    def read_masses(self) -> MassParameters:
        return MassParameters(m1=self.controls.get_value("m1"),
                              m2=self.controls.get_value("m2"))

    def write_masses(self, masses: MassParameters) -> None:
        self.controls.set_value("m1", masses.m1)
        self.controls.set_value("m2", masses.m2)