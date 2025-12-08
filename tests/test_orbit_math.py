"""Numerical tests for the low-level orbital mechanics helpers."""

from __future__ import annotations

import numpy as np
import pytest

from orbel_app.core.orbit_math import (
    E_from_nu,
    M_from_E,
    Rx,
    Rz,
    nu_from_E,
    solve_kepler,
)


def test_rotation_matrices_are_orthogonal_and_inverse_transpose():
    theta = 0.73
    for R in (Rz(theta), Rx(theta)):
        should_be_identity = R @ R.T
        assert np.allclose(should_be_identity, np.eye(3), atol=1e-12)


def test_kepler_round_trip_M_to_E_and_back():
    e = 0.3
    M = np.linspace(0.0, 2 * np.pi, 8)
    E = solve_kepler(M, e)
    M_back = M_from_E(E, e)
    assert np.allclose(M_back, M, atol=1e-10)


@pytest.mark.parametrize("e", [0.0, 0.2, 0.7])
def test_true_eccentric_mean_anomaly_cycles_are_consistent(e: float):
    nu = np.linspace(-np.pi, np.pi, 9)
    E = E_from_nu(nu, e)
    nu_back = nu_from_E(E, e)
    assert np.allclose(np.unwrap(nu_back), np.unwrap(nu), atol=1e-10)

