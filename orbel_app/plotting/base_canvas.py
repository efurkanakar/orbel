"""Core Matplotlib canvas that draws the shared 3D and 2D orbit views."""

import numpy as np
from typing import Dict, Tuple, Optional

import matplotlib.pyplot as plt

from ..core.orbit_math import (E_from_nu, M_from_E, Rz, Rx, nu_from_E, solve_kepler)
from .models import OrbitParameters, MassParameters, OrbitModel
from .plot_cards import create_plot_cards
from .axis_setup import configure_axes
from .artist_factory import create_artists
from .decor_mixins import OrbitDecorMixin
from .visibility_controller import VisibilityController, VisibilityContext
from .protocols import DecorHostProtocol, VisibilityHostProtocol
from .animator import OrbitAnimator

from matplotlib.ticker import FixedLocator


class OrbitCanvasBase(OrbitDecorMixin, DecorHostProtocol, VisibilityHostProtocol):
    """Shared Matplotlib canvas for 3D and 2D orbit visualisation."""

    def __init__(self, title3d: str = "3-D Orbit Geometry", title2d: str = "Sky-Plane Projection"):

        self.font_size: int = 14
        self.omega_is_primary: bool = False

        cards = create_plot_cards(title3d, title2d, self.font_size)
        self.card3d = cards.card3d
        self.card2d = cards.card2d
        self.ax3d = cards.ax3d
        self.ax2d = cards.ax2d
        self.figure3d = cards.canvas3d.figure
        self.figure2d = cards.canvas2d.figure
        self.canvas3d = cards.canvas3d
        self.canvas2d = cards.canvas2d
        self.toolbar3d = cards.toolbar3d
        self.toolbar2d = cards.toolbar2d
        self.ax3d.computed_zorder = False

        configure_axes(self.figure3d, self.figure2d, self.ax3d, self.ax2d)

        self.init_elev = 20.0
        self.init_azim = -60.0
        self.ax3d.view_init(elev=self.init_elev, azim=self.init_azim)

        artists = create_artists(self.ax3d, self.ax2d, self.font_size)
        self.center3d = artists.center3d
        self.center2d = artists.center2d
        self._axis_texts = artists.axis_texts
        self._axis_colors = artists.axis_colors
        self.i_wedge = artists.i_wedge
        self.sky_plane = artists.sky_plane
        self.orbit3d = artists.orbit3d
        self.nodes3d = artists.nodes3d
        self.asc3d = artists.asc3d
        self.des3d = artists.des3d
        self.peri3d = artists.peri3d
        self.Om_arc3d = artists.Om_arc3d
        self.w_arc3d = artists.w_arc3d
        self.body3d = artists.body3d
        self.orbit2d = artists.orbit2d
        self.nodes2d = artists.nodes2d
        self.asc2d = artists.asc2d
        self.des2d = artists.des2d
        self.peri2d = artists.peri2d
        self.Om_arc2d = artists.Om_arc2d
        self.w_arc2d = artists.w_arc2d
        self.body2d = artists.body2d
        self._body_artists = artists.body_artists
        self.visibility = VisibilityController(
            VisibilityContext(
                set_flag=lambda attr, val: setattr(self, attr, val),
                get_flag=lambda attr: bool(getattr(self, attr, False)),
                redraw=self._redraw,
                node_artists=(self.asc3d, self.des3d, self.asc2d, self.des2d),
                line_node_artists=(self.nodes3d, self.nodes2d),
                update_periastron=self._update_periastron,
                update_nodes=self._update_nodes,
                update_Om_arc=self._update_Om_arc,
                update_w_arc=self._update_w_arc,
                update_i_wedge=self._update_i_wedge,
                update_sky_label=self._update_sky_label_patch,
                clear_sky_label=self._clear_sky_label_patch,
                clear_ref_quivers=self._clear_ref_quivers,
                update_axes_limits=self._update_axes_limits,
                update_ne_guides=self._update_NE_guides,
                axis_texts=self._axis_texts,
                sky_plane=self.sky_plane,
                center3d=self.center3d,
                center2d=self.center2d,
                body_artists=self._body_artists,
            )
        )

        self._show_centers = True

        self.canvas3d.mpl_connect("draw_event", lambda evt: self._place_axis_labels())
        self.axis_label_xy_scale = 1.0
        self.los_arrow_scale = 1.35

        self._ne_lines = None
        self._ref_quivers = []

        self._sky_label_patch = None
        self._corner_lines = []

        self.init = dict(
            a=1.0,
            e=0.5,
            i=np.deg2rad(45.0),
            w=np.deg2rad(90.0),
            Om=np.deg2rad(90.0),
            m1=1.6,
            m2=0.8,
            start_nu=np.deg2rad(45.0),
        )

        initial_orbit = OrbitParameters(
            a=self.init["a"],
            e=self.init["e"],
            i=self.init["i"],
            w=self.init["w"],
            Om=self.init["Om"],
            start_nu=self.init["start_nu"],
        )
        initial_mass = MassParameters(m1=self.init["m1"], m2=self.init["m2"])
        self.orbit_model = OrbitModel(initial_orbit, initial_mass)
        self.orbit_model.subscribe("orbit", self._on_orbit_model_changed)
        self.orbit_model.subscribe("mass", self._on_mass_model_changed)

        self.nu = float(self.start_nu)
        E0 = E_from_nu(self.nu, self.e)
        self.M = float(M_from_E(E0, self.e))

        self.animator = OrbitAnimator(self)
        self.animator.recompute_mean_motion()

        self.ax2d.grid(True, which="both", linestyle=":", alpha=0.25, linewidth=0.8)

        self.lock_axes_limits = False
        self._L_locked = None
        self._L = None

        self.min_expand_factor = 1.15
        self.max_shrink_factor = 0.90

        self._show_nodes = True
        self._show_line_nodes = True
        self._show_Om = True
        self._show_omega = True
        self._show_i_wedge = True
        self._show_axis_triad = True
        self._show_sky_plane = True
        self._show_ne_guides = True
        self._show_sky_label = True
        self._show_bodies = True

    @property
    def orbit_params(self) -> OrbitParameters:
        return self.orbit_model.orbit

    @property
    def mass_params(self) -> MassParameters:
        return self.orbit_model.masses

    @property
    def a(self) -> float:
        return self.orbit_params.a

    @a.setter
    def a(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(a=value), keep_phase=True)

    @property
    def e(self) -> float:
        return self.orbit_model.orbit.e

    @e.setter
    def e(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(e=value), keep_phase=True)

    @property
    def i(self) -> float:
        return self.orbit_model.orbit.i

    @i.setter
    def i(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(i=value), keep_phase=True)

    @property
    def w(self) -> float:
        return self.orbit_model.orbit.w

    @w.setter
    def w(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(w=value), keep_phase=True)

    @property
    def Om(self) -> float:
        return self.orbit_model.orbit.Om

    @Om.setter
    def Om(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(Om=value), keep_phase=True)

    @property
    def start_nu(self) -> float:
        return self.orbit_model.orbit.start_nu

    @start_nu.setter
    def start_nu(self, value: float) -> None:
        self.apply_parameters(self.orbit_params.with_updates(start_nu=value), keep_phase=False)

    def _on_orbit_model_changed(self, params: OrbitParameters) -> None:
        self.recompute_mean_motion()

    def _on_mass_model_changed(self, masses: MassParameters) -> None:
        self.recompute_mean_motion()

    @property
    def m1(self) -> float:
        return self.orbit_model.masses.m1

    @m1.setter
    def m1(self, value: float) -> None:
        self.orbit_model.update_masses(m1=value)

    @property
    def m2(self) -> float:
        return self.orbit_model.masses.m2

    @m2.setter
    def m2(self, value: float) -> None:
        self.orbit_model.update_masses(m2=value)

    def lock_axes(self, lock: bool = True, L: Optional[float] = None) -> None:
        self.lock_axes_limits = bool(lock)
        if self.lock_axes_limits:
            if L is not None:
                self._L_locked = float(L)
            elif getattr(self, "_L", None) is not None:
                self._L_locked = float(self._L)
            else:
                self._L_locked = None
        else:
            self._L_locked = None

        self._update_axes_limits()
        self._redraw()

    def _redraw(self) -> None:
        self.canvas3d.draw_idle()
        self.canvas2d.draw_idle()

    def set_centers_visible(self, visible: bool) -> None:
        self.visibility.set_centers_visible(visible)

    def set_nodes_visible(self, visible: bool) -> None:
        self.visibility.set_nodes_visible(visible)

    def set_line_of_nodes_visible(self, visible: bool) -> None:
        self.visibility.set_line_of_nodes_visible(visible)

    def set_Omega_visible(self, visible: bool) -> None:
        self.visibility.set_Omega_visible(visible)

    def set_omega_visible(self, visible: bool) -> None:
        self.visibility.set_omega_visible(visible)

    def set_inclination_visible(self, visible: bool) -> None:
        self.visibility.set_inclination_visible(visible)

    def set_skyplane_label_visible(self, visible: bool) -> None:
        self.visibility.set_skyplane_label_visible(visible)

    def set_sky_plane_visible(self, visible: bool) -> None:
        self.visibility.set_sky_plane_visible(visible)

    def set_reference_axes_visible(self, visible: bool) -> None:
        self.visibility.set_reference_axes_visible(visible)

    def set_ne_guides_visible(self, visible: bool) -> None:
        self.visibility.set_ne_guides_visible(visible)

    def set_bodies_visible(self, visible: bool) -> None:
        self.visibility.set_bodies_visible(visible)

    def _rotmat(self) -> np.ndarray:
        return self.orbit_params.rotation_matrix(self.omega_is_primary)

    def _orbital_xyz_rel(self, f: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.orbit_params.relative_position(f, omega_is_primary=self.omega_is_primary)
    
    #--------------------------------------------

    def _to_sky2d(self, X, Y):
        return (np.asarray(Y), np.asarray(X))

    def _update_nodes(self) -> None:
        t = np.array([-0.9 * self._L, 0.9 * self._L])
        x_nd = t * np.cos(self.Om)
        y_nd = t * np.sin(self.Om)
        self.nodes3d.set_data(x_nd, y_nd)
        self.nodes3d.set_3d_properties(np.zeros_like(t))
        u, v = self._to_sky2d(x_nd, y_nd)
        self.nodes2d.set_data(u, v)
        self.nodes3d.set_visible(self._show_line_nodes)
        self.nodes2d.set_visible(self._show_line_nodes)

    def _update_Om_arc(self) -> None:
        Om = self.Om % (2 * np.pi)
        if Om < 1e-9 or not self._show_Om:
            self.Om_arc3d.set_data([], [])
            self.Om_arc3d.set_3d_properties([])
            self.Om_arc2d.set_data([], [])
            return
        th = np.linspace(0, (2 * np.pi if abs(Om - 2 * np.pi) < 1e-9 else Om), 200, endpoint=True)
        r = 0.7 * self._L
        xO, yO = r * np.cos(th), r * np.sin(th)
        self.Om_arc3d.set_data(xO, yO)
        self.Om_arc3d.set_3d_properties(np.zeros_like(th))
        uO, vO = self._to_sky2d(xO, yO)
        self.Om_arc2d.set_data(uO, vO)
        self.Om_arc3d.set_visible(True)
        self.Om_arc2d.set_visible(True)

    def _omega_arc_points(self, w: float) -> np.ndarray:
        dir_sign = +1.0 if self.i < (0.5 * np.pi) else -1.0
        f_asc = (-w) % (2 * np.pi) if dir_sign > 0 else (w % (2 * np.pi))
        th = np.linspace(0, w, 200, endpoint=True)
        return (f_asc + dir_sign * th) % (2 * np.pi)

    def _dir_sign(self) -> float:
        return +1.0 if self.i < (0.5 * np.pi) else -1.0

    def _recompute_from_M(self) -> None:
        E = solve_kepler(self.M, self.e)
        self.nu = float(nu_from_E(E, self.e))

    def _set_nu_keep_phase(self, nu_new: float) -> None:
        self.nu = float(nu_new)
        E = E_from_nu(self.nu, self.e)
        self.M = float(M_from_E(E, self.e))

    def recompute_mean_motion(self) -> None:
        self.animator.recompute_mean_motion()

    def start(self) -> None:
        self.animator.start()

    def stop(self) -> None:
        self.animator.stop()

    def apply_font_size(self, size: int, *, redraw: bool = True) -> None:
        self.font_size = int(size)
        plt.rcParams.update({
            "font.size": self.font_size,
            "axes.titlesize": self.font_size + 1,
            "axes.labelsize": self.font_size,
            "xtick.labelsize": max(8, self.font_size - 1),
            "ytick.labelsize": max(8, self.font_size - 1),
        })
        for ax in (self.ax3d, self.ax2d):
            ax.tick_params(axis="both", which="both", labelsize=max(8, self.font_size - 1))
        for txt in self._axis_texts.values():
            txt.set_fontsize(self.font_size)

        self._update_sky_label_patch()

        if redraw:
            self._redraw()


    def apply_parameters(self, params: OrbitParameters, *, keep_phase: bool) -> None:
        params = params.ensure_valid()
        current_nu = float(getattr(self, "nu", params.start_nu))
        self.orbit_model.set_orbit(params)
        target_nu = current_nu if keep_phase else params.start_nu
        self._set_nu_keep_phase(target_nu)
        self._update_axes_limits()
        self.update_all()

    def apply_masses(self, masses: MassParameters) -> None:
        self.orbit_model.set_masses(masses)
        self.update_all()

    def _update_orbit_curves(self) -> None:
        raise NotImplementedError

    def _update_periastron(self) -> None:
        raise NotImplementedError

    def _update_w_arc(self) -> None:
        raise NotImplementedError
    
    def _update_body_only(self) -> None:
        raise NotImplementedError

    def _update_i_wedge(self) -> None:
        if not self._show_i_wedge:
            self.i_wedge.set_visible(False)
            return

        k = np.array([0.0, 0.0, 1.0])
        n = self._rotmat() @ k
        axis = np.cross(k, n)
        s = np.linalg.norm(axis)
        if s < 1e-9:
            self.i_wedge.set_visible(False)
            return

        l_hat = axis / s
        e1 = np.cross(l_hat, k)
        e1 /= np.linalg.norm(e1)
        ths = np.linspace(0.0, float(self.i), 40)
        rim = np.vstack([np.cos(th) * e1 + np.sin(th) * np.cross(l_hat, e1) for th in ths])
        verts = np.vstack((np.zeros(3), 0.7 * self._L * rim))
        self.i_wedge.set_verts([verts])
        self.i_wedge.set_alpha(0.30)
        self.i_wedge.set_visible(True)

    def set_limits(self, L: float) -> None:
        self._L = float(L)
        self.lock_axes(True, self._L)
        self.ax3d.set(xlim=(-L, L), ylim=(-L, L), zlim=(-L, L))
        self.ax2d.set_xlim(L, -L)
        self.ax2d.set_ylim(-L, L)
        self._update_NE_guides()
        self._update_sky_label_patch()
        self._draw_corner_grid()
        self._redraw()

    def set_ticks(self, count2d: int | None = None, count3d: int | None = None, step2d: float | None = None, prune_ends: bool = True) -> None:

        if count2d is not None:
            x0, x1 = self.ax2d.get_xlim()
            y0, y1 = self.ax2d.get_ylim()
            xmin, xmax = (min(x0, x1), max(x0, x1))
            ymin, ymax = (min(y0, y1), max(y0, y1))

            xs = np.linspace(xmin, xmax, count2d)
            ys = np.linspace(ymin, ymax, count2d)

            if prune_ends and count2d >= 3:
                xs = xs[1:-1]
                ys = ys[1:-1]

            self.ax2d.xaxis.set_major_locator(FixedLocator(xs))
            self.ax2d.yaxis.set_major_locator(FixedLocator(ys))

        elif step2d is not None:
            x0, x1 = self.ax2d.get_xlim()
            y0, y1 = self.ax2d.get_ylim()
            xmin, xmax = (min(x0, x1), max(x0, x1))
            ymin, ymax = (min(y0, y1), max(y0, y1))
            xs = np.arange(xmin, xmax + 1e-9, step2d)
            ys = np.arange(ymin, ymax + 1e-9, step2d)
            if prune_ends and xs.size >= 3:
                xs = xs[1:-1]
            if prune_ends and ys.size >= 3:
                ys = ys[1:-1]
            self.ax2d.xaxis.set_major_locator(FixedLocator(xs))
            self.ax2d.yaxis.set_major_locator(FixedLocator(ys))

        if count3d is not None:
            def interior_ticks(lim, n):
                a, b = lim
                lo, hi = (min(a, b), max(a, b))
                arr = np.linspace(lo, hi, n)
                if prune_ends and n >= 3:
                    arr = arr[1:-1]
                return arr

            tx = interior_ticks(self.ax3d.get_xlim(), count3d)
            ty = interior_ticks(self.ax3d.get_ylim(), count3d)
            tz = interior_ticks(self.ax3d.get_zlim(), count3d)
            self.ax3d.xaxis.set_major_locator(FixedLocator(tx))
            self.ax3d.yaxis.set_major_locator(FixedLocator(ty))
            self.ax3d.zaxis.set_major_locator(FixedLocator(tz))
        self._draw_corner_grid()
        self._redraw()

    def update_all(self) -> None:
        self._update_axes_limits()
        self._update_orbit_curves()
        self._update_nodes()
        self._update_Om_arc()
        self._update_w_arc()
        self._update_periastron()
        self._update_body_only()
        self._update_i_wedge()
        self._redraw()

__all__ = ["OrbitCanvasBase"]