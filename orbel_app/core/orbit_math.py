"""Elementary orbital mechanics helpers used by the plotting layer.
The functions here provide rotation matrices and Kepler conversions independent of any GUI code."""

from __future__ import annotations

import numpy as np

def Rz(theta: float) -> np.ndarray:
    """Rotation matrix around the z-axis."""

    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def Rx(theta: float) -> np.ndarray:
    """Rotation matrix around the x-axis."""

    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def solve_kepler(M: np.ndarray, e: float, tol: float = 1e-12, n_iter: int = 40) -> np.ndarray:
    """
    Solve Kepler's equation M = E - e sin(E) for the eccentric anomaly E.

    Parameters
    ----------
    M:
        Mean anomaly in radians.
    e:
        Orbit eccentricity (0 <= e < 1).
    tol:
        Convergence threshold for Newton iterations.
    n_iter:
        Iteration count.
    """

    E = M + e * np.sin(M)
    for _ in range(n_iter):
        f = E - e * np.sin(E) - M
        fp = 1.0 - e * np.cos(E)
        dE = f / fp
        E -= dE
        if np.all(np.abs(dE) < tol):
            break
    return E


def E_from_nu(nu: np.ndarray, e: float) -> np.ndarray:
    """Convert true anomaly to eccentric anomaly."""

    return 2.0 * np.arctan2(np.sqrt(1 - e) * np.sin(nu / 2.0),
                            np.sqrt(1 + e) * np.cos(nu / 2.0))


def M_from_E(E: np.ndarray, e: float) -> np.ndarray:
    """Mean anomaly from eccentric anomaly."""

    return E - e * np.sin(E)


def nu_from_E(E: np.ndarray, e: float) -> np.ndarray:
    """True anomaly from eccentric anomaly."""

    return 2.0 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2.0),
                            np.sqrt(1 - e) * np.cos(E / 2.0))

__all__ = [
    "Rz",
    "Rx",
    "solve_kepler",
    "E_from_nu",
    "M_from_E",
    "nu_from_E",
]