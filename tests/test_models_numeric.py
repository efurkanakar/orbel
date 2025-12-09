"""Numerical tests for OrbitParameters and MassParameters."""

from __future__ import annotations

import numpy as np
import pytest

from orbel_app.plotting.models import MassParameters, OrbitParameters


def test_orbit_parameters_relative_position_on_circular_orbit_matches_expectation():
    params = OrbitParameters(a=2.0, e=0.0, i=0.0, w=0.0, Om=0.0, start_nu=0.0)
    f = np.array([0.0, np.pi / 2, np.pi])
    pos = params.relative_position(f)

    expected = np.array(
        [
            [2.0, 0.0, -2.0],  # x
            [0.0, 2.0, 0.0],   # y
            [0.0, 0.0, 0.0],   # z
        ]
    )
    assert np.allclose(pos, expected, atol=1e-12)


def test_orbit_parameters_extent_radius_respects_eccentricity():
    p_circ = OrbitParameters(a=1.5, e=0.0, i=0.0, w=0.0, Om=0.0, start_nu=0.0)
    p_ecc = OrbitParameters(a=1.5, e=0.5, i=0.0, w=0.0, Om=0.0, start_nu=0.0)

    assert p_circ.extent_radius() == pytest.approx(1.5)
    assert p_ecc.extent_radius() == pytest.approx(1.5 * (1 + 0.5))


def test_mass_parameters_mean_motion_and_barycentric_factors():
    # Equal-mass case: factors should be symmetric about zero.
    eq = MassParameters(m1=1.0, m2=1.0)
    total_eq = eq.total_mass()
    assert total_eq == pytest.approx(2.0)
    f1_eq, f2_eq = eq.barycentric_factors()
    assert f1_eq == pytest.approx(-0.5)
    assert f2_eq == pytest.approx(0.5)

    # Unequal-mass case: barycenter lies closer to the more massive component.
    masses = MassParameters(m1=2.0, m2=1.0)
    total = masses.total_mass()
    assert total == pytest.approx(3.0)
    f1, f2 = masses.barycentric_factors()
    assert f1 == pytest.approx(-1.0 / 3.0)
    assert f2 == pytest.approx(2.0 / 3.0)

    n = masses.mean_motion(semi_major=2.0)
    expected_n = np.sqrt(total / (2.0 ** 3))
    assert n == pytest.approx(expected_n)
