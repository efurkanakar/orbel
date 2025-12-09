"""Data models for orbital parameters, masses and the observable orbit model."""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections import defaultdict
from typing import Callable, DefaultDict, Literal, Any

import numpy as np

from ..core.orbit_math import Rz, Rx

_EPS = 1e-9

@dataclass(slots=True)
class OrbitParameters:
    """Physical and orientation parameters that define a Keplerian orbit."""

    a: float
    e: float
    i: float
    w: float
    Om: float
    start_nu: float

    def ensure_valid(self) -> "OrbitParameters":
        a = max(float(self.a), _EPS)
        e = min(max(float(self.e), 0.0), 0.999999)
        i = float(self.i)
        w = float(self.w)
        Om = float(self.Om)
        nu = float(self.start_nu)
        return OrbitParameters(a=a, e=e, i=i, w=w, Om=Om, start_nu=nu)

    def with_updates(self, **kwargs) -> "OrbitParameters":
        return replace(self, **kwargs).ensure_valid()

    def rotation_matrix(self, omega_is_primary: bool = False) -> np.ndarray:
        arg_w = self.w if not omega_is_primary else self.w + np.pi
        return Rz(self.Om) @ Rx(self.i) @ Rz(arg_w)

    def relative_position(self, f: np.ndarray, omega_is_primary: bool = False) -> np.ndarray:
        """Return 3×N coordinates in the inertial frame for given true anomalies."""
        r = self.a * (1 - self.e ** 2) / (1 + self.e * np.cos(f))
        x, y = r * np.cos(f), r * np.sin(f)
        rot = self.rotation_matrix(omega_is_primary=omega_is_primary)
        return rot @ np.vstack((x, y, np.zeros_like(x)))

    def extent_radius(self) -> float:
        return max(self.a * (1 + self.e), _EPS)


@dataclass(slots=True)
class MassParameters:
    """Mass pair for the binary system and derived barycentric factors."""

    m1: float
    m2: float

    def ensure_valid(self) -> "MassParameters":
        return MassParameters(m1=max(float(self.m1), _EPS), m2=max(float(self.m2), _EPS))

    def with_updates(self, **kwargs) -> "MassParameters":
        return replace(self, **kwargs).ensure_valid()

    def total_mass(self) -> float:
        return max(self.m1 + self.m2, _EPS)

    def barycentric_factors(self) -> tuple[float, float]:
        total = self.total_mass()
        return (-self.m2 / total, self.m1 / total)

    def mean_motion(self, semi_major: float) -> float:
        semi = max(float(semi_major), _EPS)
        return np.sqrt(self.total_mass() / (semi ** 3))


class OrbitModel:
    """Observable wrapper that stores orbit/mass parameters and notifies listeners."""

    def __init__(self, orbit: OrbitParameters, masses: MassParameters) -> None:
        self._orbit = orbit.ensure_valid()
        self._mass = masses.ensure_valid()
        self._listeners: DefaultDict[str, list[Callable[[Any], None]]] = defaultdict(list)

    @property
    def orbit(self) -> OrbitParameters:
        return self._orbit

    @property
    def masses(self) -> MassParameters:
        return self._mass

    def subscribe(self, topic: Literal["orbit", "mass"], callback: Callable[[Any], None]) -> None:
        self._listeners[topic].append(callback)

    def _notify(self, topic: Literal["orbit", "mass"]) -> None:
        value = self._orbit if topic == "orbit" else self._mass
        for callback in self._listeners.get(topic, []):
            callback(value)

    def set_orbit(self, params: OrbitParameters) -> None:
        self._orbit = params.ensure_valid()
        self._notify("orbit")

    def update_orbit(self, **kwargs) -> None:
        self.set_orbit(self._orbit.with_updates(**kwargs))

    def set_masses(self, masses: MassParameters) -> None:
        self._mass = masses.ensure_valid()
        self._notify("mass")

    def update_masses(self, **kwargs) -> None:
        self.set_masses(self._mass.with_updates(**kwargs))