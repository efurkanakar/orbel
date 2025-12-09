"""
PyQt5 + Matplotlib-based relative orbit visualizer.
This module renders the 3D orbit geometry and its sky-plane projection.
It defines "RelativeCanvas", a subclass of "OrbitCanvasBase".
"""

import numpy as np
from .base_canvas import OrbitCanvasBase

class RelativeCanvas(OrbitCanvasBase):
    """Canvas that visualises the relative orbit geometry."""
    def __init__(self):
        super().__init__(title3d="3-D Orbit Geometry", title2d="Sky-Plane Projection")
        self.update_all()

    @staticmethod
    def _as_tuple(x):
        return (float(x),)

    def _set_point_3d(self, artist, x, y, z):
        artist.set_data(self._as_tuple(x), self._as_tuple(y))
        artist.set_3d_properties(self._as_tuple(z))

    def _set_point_2d(self, artist, x, y):
        u, v = self._to_sky2d(np.array([x]), np.array([y]))
        artist.set_data(u, v)

    # ----------------------------------------------------------------------------------

    def _update_orbit_curves(self) -> None:

        f = np.linspace(0, 2 * np.pi, 1000)
        X, Y, Z = self._orbital_xyz_rel(f)
        self.orbit3d.set_data(X, Y)
        self.orbit3d.set_3d_properties(Z)
        u2d, v2d = self._to_sky2d(X, Y)
        self.orbit2d.set_data(u2d, v2d)

    def _update_periastron(self) -> None:

        Xp, Yp, Zp = self._orbital_xyz_rel(np.array([0.0]))

        xp = Xp.item()
        yp = Yp.item()
        zp = Zp.item()

        self._set_point_3d(self.peri3d, xp, yp, zp)
        self._set_point_2d(self.peri2d, xp, yp)

        w_eff = self.w % (2 * np.pi)
        f_asc = (-w_eff) % (2 * np.pi)
        f_des = (np.pi - w_eff) % (2 * np.pi)

        Xa, Ya, Za = self._orbital_xyz_rel(np.array([f_asc]))
        Xd, Yd, Zd = self._orbital_xyz_rel(np.array([f_des]))

        xa = Xa.item()
        ya = Ya.item() 
        za = Za.item()

        xd = Xd.item()
        yd = Yd.item()
        zd = Zd.item()

        self._set_point_3d(self.asc3d, xa, ya, za)
        self._set_point_3d(self.des3d, xd, yd, zd)
        self._set_point_2d(self.asc2d, xa, ya)
        self._set_point_2d(self.des2d, xd, yd)

    def _update_w_arc(self) -> None:

        w = self.w % (2 * np.pi)

        f_arc = self._omega_arc_points(w)

        Xw, Yw, Zw = self._orbital_xyz_rel(f_arc)

        eps = getattr(self, "arc_eps", 0.0)
        if eps:
            n = self._rotmat() @ np.array([0.0, 0.0, 1.0])
            Xw = Xw + eps * n[0]
            Yw = Yw + eps * n[1]
            Zw = Zw + eps * n[2]

        self.w_arc3d.set_data(Xw, Yw)
        self.w_arc3d.set_3d_properties(Zw)

        uw, vw = self._to_sky2d(Xw, Yw)
        self.w_arc2d.set_data(uw, vw)

    def _update_body_only(self) -> None:

        Xb, Yb, Zb = self._orbital_xyz_rel(np.array([self.nu]))

        xb = Xb.item()
        yb = Yb.item()
        zb = Zb.item()

        self.body3d._offsets3d = (np.array([xb]), np.array([yb]), np.array([zb]))

        ub, vb = self._to_sky2d(np.array([xb]), np.array([yb]))

        self.body2d.set_offsets(np.column_stack((ub, vb)))

__all__ = ["RelativeCanvas"]