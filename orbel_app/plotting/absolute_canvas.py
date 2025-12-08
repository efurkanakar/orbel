"""
PyQt5 + Matplotlib-based absolute orbit visualizer.
This module draws the 3D orbit geometry and the 2D projected orbits
for both bodies around the barycenter. It defines "AbsoluteCanvas",
a subclass of "OrbitCanvasBase".
"""

import numpy as np
from .base_canvas import OrbitCanvasBase

class AbsoluteCanvas(OrbitCanvasBase):
    """Canvas that visualises absolute orbits about the barycenter."""

    def __init__(self):
        super().__init__(title3d="3-D Orbit Geometry", title2d="Projected Orbits")
        self._show_peri_link = True

        self.center3d.remove()
        self.center2d.remove()
        self.center3d = self.ax3d.scatter(0, 0, 0, marker="x", c="black", s=80, zorder=8)
        self.center2d = self.ax2d.scatter(0, 0, marker="x", c="black", s=80, zorder=8)

        (self.orbit1_3d,) = self.ax3d.plot([], [], [],   color="salmon", lw=1.5, linestyle="--", zorder=2)
        (self.orbit2_3d,) = self.ax3d.plot([], [], [],   color="black",  lw=1.5, linestyle="--", zorder=2)
        (self.orbit1_2d,) = self.ax2d.plot([], [],       color="salmon", lw=1.5, linestyle="--", zorder=2)
        (self.orbit2_2d,) = self.ax2d.plot([], [],       color="black",  lw=1.5, linestyle="--", zorder=2)

        self.body3d.remove()
        self.body2d.remove()
        self.body1_3d = self.ax3d.scatter([], [], [],    color="darkred",    s=50, zorder=11)
        self.body2_3d = self.ax3d.scatter([], [], [],    color="navy", s=50, zorder=11)
        self.body1_2d = self.ax2d.scatter([], [],        color="darkred",    s=50, zorder=11)
        self.body2_2d = self.ax2d.scatter([], [],        color="navy", s=50, zorder=11)

        self._body_artists = [self.body1_3d, self.body2_3d, self.body1_2d, self.body2_2d]

        self.peri1_3d, = self.ax3d.plot([], [], [], "d", color="gold", ms=8, zorder=14)
        self.peri2_3d, = self.ax3d.plot([], [], [], "d", color="gold", ms=8, zorder=14)
        self.peri1_2d, = self.ax2d.plot([], [],     "d", color="gold", ms=8, zorder=14)
        self.peri2_2d, = self.ax2d.plot([], [],     "d", color="gold", ms=8, zorder=14)
        self.peri_link3d, = self.ax3d.plot([], [], [],   color="seagreen", lw=1.4, zorder=11)

        self.peri_link3d.set_visible(self._show_peri_link)

        self.set_centers_visible(getattr(self, "_show_centers", True))

        (self.w1_arc3d,) = self.ax3d.plot([], [], [], color="blue", lw=2, zorder=6)
        (self.w2_arc3d,) = self.ax3d.plot([], [], [], color="red",  lw=2, zorder=6)

        (self.w1_arc2d,) = self.ax2d.plot([], [],     color="blue", lw=2, zorder=11)
        (self.w2_arc2d,) = self.ax2d.plot([], [],     color="red",  lw=2, zorder=11)

        self.update_all()

    def _split_absolute(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray):

        m1 = self.m1
        m2 = self.m2
        c1 = -m2 / (m1 + m2)
        c2 = m1 / (m1 + m2)

        return c1 * X, c1 * Y, c1 * Z, c2 * X, c2 * Y, c2 * Z, c1, c2

    def set_centers_visible(self, visible: bool) -> None:
        super().set_centers_visible(visible)
        self._update_periastron()

    def set_peri_link_visible(self, visible: bool) -> None:
        self._show_peri_link = bool(visible)
        if not self._show_peri_link and getattr(self, "peri_link3d", None) is not None:
            self.peri_link3d.set_visible(False)
        else:
            self._update_periastron()
        self._redraw()

    def _update_orbit_curves(self) -> None:
        f_line = np.linspace(0, 2 * np.pi, 1000)
        Xr, Yr, Zr = self._orbital_xyz_rel(f_line)
        X1, Y1, Z1, X2, Y2, Z2, _, _ = self._split_absolute(Xr, Yr, Zr)
        
        self.orbit1_3d.set_data(X1, Y1)
        self.orbit1_3d.set_3d_properties(Z1)
        
        self.orbit2_3d.set_data(X2, Y2)
        self.orbit2_3d.set_3d_properties(Z2)
        
        u1, v1 = self._to_sky2d(X1, Y1)
        u2, v2 = self._to_sky2d(X2, Y2)
        
        self.orbit1_2d.set_data(u1, v1)
        self.orbit2_2d.set_data(u2, v2)

    def _update_periastron(self) -> None:
        Xp, Yp, Zp = self._orbital_xyz_rel(np.array([0.0]))
        x1p, y1p, z1p, x2p, y2p, z2p, c1, c2 = self._split_absolute(Xp, Yp, Zp)

        self.peri1_3d.set_data([x1p[0]], [y1p[0]])
        self.peri1_3d.set_3d_properties([z1p[0]])
        
        self.peri2_3d.set_data([x2p[0]], [y2p[0]])
        self.peri2_3d.set_3d_properties([z2p[0]])

        u1p, v1p = self._to_sky2d([x1p[0]], [y1p[0]])
        u2p, v2p = self._to_sky2d([x2p[0]], [y2p[0]])
        
        self.peri1_2d.set_data(u1p, v1p)
        self.peri2_2d.set_data(u2p, v2p)
        
        if self._show_peri_link:
            self.peri_link3d.set_data([x1p[0], x2p[0]], [y1p[0], y2p[0]])
            self.peri_link3d.set_3d_properties([z1p[0], z2p[0]])
            self.peri_link3d.set_visible(True)
        else:
            self.peri_link3d.set_visible(False)

        w_eff = self.w % (2 * np.pi)
        f_asc = (-w_eff) % (2 * np.pi)        
        f_des = (np.pi - w_eff) % (2 * np.pi) 
        
        Xa_rel, Ya_rel, Za_rel = self._orbital_xyz_rel(np.array([f_asc]))
        Xd_rel, Yd_rel, Zd_rel = self._orbital_xyz_rel(np.array([f_des]))

        x1a, y1a, z1a, x2a, y2a, z2a, c1, c2 = self._split_absolute(Xa_rel, Ya_rel, Za_rel)
        x1d, y1d, z1d, x2d, y2d, z2d, _, _  = self._split_absolute(Xd_rel, Yd_rel, Zd_rel)

        use_1 = (abs(c1) >= abs(c2))

        if use_1:

            xA = x1a[0]
            yA = y1a[0]
            zA = z1a[0]

            xD = x1d[0]
            yD = y1d[0]
            zD = z1d[0]

        else:

            xA = x2a[0]
            yA = y2a[0]
            zA = z2a[0]

            xD = x2d[0]
            yD = y2d[0] 
            zD = z2d[0]

        self.asc3d.set_data([xA], [yA])
        self.asc3d.set_3d_properties([zA])

        self.des3d.set_data([xD], [yD])
        self.des3d.set_3d_properties([zD])

        uA, vA = self._to_sky2d([xA], [yA])
        uD, vD = self._to_sky2d([xD], [yD])
        
        self.asc2d.set_data(uA, vA)
        self.des2d.set_data(uD, vD)

        self.asc3d.set_visible(self._show_nodes)
        self.des3d.set_visible(self._show_nodes)
        
        self.asc2d.set_visible(self._show_nodes)
        self.des2d.set_visible(self._show_nodes)

    def _update_w_arc(self) -> None:
        
        if not self._show_omega:
            for ln in (self.w1_arc3d, self.w2_arc3d, self.w1_arc2d, self.w2_arc2d):
                ln.set_data([], [])
            self.w1_arc3d.set_3d_properties([]); self.w2_arc3d.set_3d_properties([])
            self.w1_arc2d.set_visible(False); self.w2_arc2d.set_visible(False)
            return

        w_salmon = self.w % (2*np.pi)
        w_black  = (w_salmon + np.pi) % (2*np.pi)

        arc_eps = getattr(self, "arc_eps", 0.0)
        n = self._rotmat() @ np.array([0.0, 0.0, 1.0]) if arc_eps != 0.0 else None

        def make_component_arc(w: float, pick_component: int):

            f = self._omega_arc_points(w)
            Xr, Yr, Zr = self._orbital_xyz_rel(f)
            
            if arc_eps != 0.0:
                Xr = Xr + arc_eps * n[0]
                Yr = Yr + arc_eps * n[1]
                Zr = Zr + arc_eps * n[2]
            
            x1, y1, z1, x2, y2, z2, _, _ = self._split_absolute(Xr, Yr, Zr)
            
            return (x1, y1, z1) if pick_component == 1 else (x2, y2, z2)

        x2, y2, z2 = make_component_arc(w_salmon, 2)
        x1, y1, z1 = make_component_arc(w_black,  1)

        self.w1_arc3d.set_data(x2, y2)
        self.w1_arc3d.set_3d_properties(z2)
        
        self.w2_arc3d.set_data(x1, y1)
        self.w2_arc3d.set_3d_properties(z1)

        if x2.size > 0:
            u2, v2 = self._to_sky2d(x2, y2)
            self.w1_arc2d.set_data(u2, v2); self.w1_arc2d.set_visible(True)
        else:
            self.w1_arc2d.set_data([], []); self.w1_arc2d.set_visible(False)

        if x1.size > 0:
            u1, v1 = self._to_sky2d(x1, y1)
            self.w2_arc2d.set_data(u1, v1); self.w2_arc2d.set_visible(True)
        else:
            self.w2_arc2d.set_data([], []); self.w2_arc2d.set_visible(False)

    def _update_body_only(self) -> None:
        nu = self.nu
        Xr, Yr, Zr = self._orbital_xyz_rel(np.array([nu]))
        x1, y1, z1, x2, y2, z2, _, _ = self._split_absolute(Xr, Yr, Zr)

        self.body1_3d._offsets3d = (x1, y1, z1)
        self.body2_3d._offsets3d = (x2, y2, z2)

        u1, v1 = self._to_sky2d(x1, y1)
        u2, v2 = self._to_sky2d(x2, y2)
        self.body1_2d.set_offsets(np.column_stack((u1, v1)))
        self.body2_2d.set_offsets(np.column_stack((u2, v2)))

__all__ = ["AbsoluteCanvas"]