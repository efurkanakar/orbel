"""Shared helpers for sky-plane labels, guides, and other orbit canvas decorations."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from mpl_toolkits.mplot3d import art3d, proj3d
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocols import DecorHostProtocol


class OrbitDecorMixin:
    """Manages sky-plane labels, axis labels, guides and other decorations."""

    def _clear_sky_label_patch(self: "DecorHostProtocol"):
        patch = getattr(self, "_sky_label_patch", None)
        if patch is not None:
            try:
                patch.remove()
            except Exception:
                pass
        self._sky_label_patch = None

    def _update_sky_label_patch(self: "DecorHostProtocol"):
        if not getattr(self, "_show_sky_label", True):
            self._clear_sky_label_patch()
            return

        L = max(getattr(self, "_L", 1.0), 1e-6)

        pad_frac = 0.06
        pad = pad_frac * L

        self._clear_sky_label_patch()

        text = "Sky Plane"
        tp = TextPath((0, 0), text, size=1.0, prop=None)

        bb_src = tp.get_extents()
        src_w = bb_src.width if bb_src.width > 1e-9 else 1.0
        target_w = 0.45 * L
        s = target_w / src_w

        trans_sr = (mtrans.Affine2D().scale(s, s).rotate_deg(90))
        tp_rot = trans_sr.transform_path(tp)

        bb_rot = tp_rot.get_extents()
        tx = (-L + pad) - bb_rot.xmin
        ty = (-L + pad) - bb_rot.ymin

        trans_final = trans_sr + mtrans.Affine2D().translate(tx, ty)
        tp_final = trans_final.transform_path(tp)

        patch = PathPatch(tp_final, facecolor="#0f766e", edgecolor="none", alpha=0.95, zorder=2)
        self.ax3d.add_patch(patch)
        art3d.pathpatch_2d_to_3d(patch, z=0.0, zdir="z")
        self._sky_label_patch = patch

    def _update_NE_guides(self: "DecorHostProtocol") -> None:
        if getattr(self, "_ne_lines", None) is None:
            lineE, = self.ax2d.plot([], [], "-", color="0.45", alpha=0.35, lw=1.0, zorder=1)
            lineN, = self.ax2d.plot([], [], "-", color="0.45", alpha=0.35, lw=1.0, zorder=1)
            labE = self.ax2d.text(
                0, 0, "E", ha="left", va="center", fontsize=12, color="0.25", alpha=0.9, zorder=2
            )
            labN = self.ax2d.text(
                0, 0, "N", ha="center", va="bottom", fontsize=12, color="0.25", alpha=0.9, zorder=2
            )
            self._ne_lines = (lineE, lineN, labE, labN)

        lineE, lineN, labE, labN = self._ne_lines
        if not self._show_ne_guides:
            for art in (lineE, lineN, labE, labN):
                art.set_visible(False)
            return

        L = self._L
        lineE.set_data([-L, L], [0, 0])
        lineN.set_data([0, 0], [-L, L])

        labN.set_position((0, 0.92 * L))
        labE.set_position((+0.92 * L, 0))
        labE.set_ha("left")

        for art in (lineE, lineN, labE, labN):
            art.set_visible(True)

    def _clear_corner_grid(self: "DecorHostProtocol"):
        for ln in getattr(self, "_corner_lines", []):
            try:
                ln.remove()
            except Exception:
                pass
        self._corner_lines = []

    def _draw_corner_grid(self: "DecorHostProtocol"):
        self._clear_corner_grid()

        gi = self.ax3d.xaxis._axinfo["grid"]
        color = gi.get("color", plt.rcParams["grid.color"])
        lw = gi.get("linewidth", plt.rcParams["grid.linewidth"])
        ls = gi.get("linestyle", plt.rcParams.get("grid.linestyle", "-"))

        xlo, xhi = sorted(self.ax3d.get_xlim())
        ylo, yhi = sorted(self.ax3d.get_ylim())
        zlo, zhi = sorted(self.ax3d.get_zlim())
        x0, y0, z0 = xlo, yhi, zlo

        self._corner_lines += [
            self.ax3d.plot([x0, xhi], [y0, y0], [z0, z0], ls=ls, lw=lw, color=color, clip_on=False)[0],
            self.ax3d.plot([x0, x0], [y0, ylo], [z0, z0], ls=ls, lw=lw, color=color, clip_on=False)[0],
            self.ax3d.plot([x0, x0], [y0, y0], [z0, zhi], ls=ls, lw=lw, color=color, clip_on=False)[0],
        ]

        self.canvas3d.draw_idle()

    def _proj_axes_xy(self: "DecorHostProtocol", x: float, y: float, z: float) -> tuple[float, float]:
        X2, Y2, _ = proj3d.proj_transform(x, y, z, self.ax3d.get_proj())
        x_disp, y_disp = self.ax3d.transData.transform((X2, Y2))
        return self.ax3d.transAxes.inverted().transform((x_disp, y_disp))

    def _place_axis_labels(self: "DecorHostProtocol") -> None:
        if not self._show_axis_triad:
            for lbl in self._axis_texts.values():
                lbl.set_visible(False)
            return

        L = self._L
        ln = getattr(self, "_arrow_len", 0.9 * L)
        los_ln = getattr(self, "_arrow_len_los", ln)
        pad = 0.15 * L
        base_offset = ln + pad
        base_offset_los = los_ln + 0.5 * pad

        xy_scale = getattr(self, "axis_label_xy_scale", 1.0)
        tips = {
            "North": (xy_scale * base_offset, 0.0, 0.0),
            "East": (0.0, xy_scale * base_offset, 0.0),
            "LoS": (0.0, 0.0, base_offset_los),
        }

        for name, (x, y, z) in tips.items():
            axx, axy = self._proj_axes_xy(x, y, z)
            axx = min(max(axx, -0.05), 1.05)
            axy = min(max(axy, -0.05), 1.05)
            txt = self._axis_texts[name]
            txt.set_visible(True)
            txt.set_color(self._axis_colors.get(name, "black"))
            txt.set_position((axx, axy))

    def _clear_ref_quivers(self: "DecorHostProtocol") -> None:
        for q in getattr(self, "_ref_quivers", []):
            try:
                q.remove()
            except Exception:
                pass
        self._ref_quivers = []

    def set_arc_epsilon(self: "DecorHostProtocol", eps: float = 0.0) -> None:
        self.arc_eps = float(eps)
        self._update_w_arc()
        self._redraw()

    def _update_axes_limits(self: "DecorHostProtocol") -> None:
        if getattr(self, "lock_axes_limits", False) and getattr(self, "_L_locked", None) is not None:
            L = float(self._L_locked)
            self._L = L
            self.ax3d.set(xlim=(-L, L), ylim=(-L, L), zlim=(-L, L))
            self.ax2d.set_xlim(L, -L)
            self.ax2d.set_ylim(-L, L)
        else:
            L = float(getattr(self, "_L", None) or (self.a * (1 + self.e)))
            if L <= 0:
                L = 1.0
            self._L = L
            self.ax3d.set(xlim=(-L, L), ylim=(-L, L), zlim=(-L, L))
            self.ax2d.set_xlim(L, -L)
            self.ax2d.set_ylim(-L, L)

        plane = [(-L, -L, 0.0), (L, -L, 0.0), (L, L, 0.0), (-L, L, 0.0)]

        self.sky_plane.set_verts([np.array(plane)])
        self.sky_plane.set_visible(self._show_sky_plane)
        self._update_sky_label_patch()

        if self._show_axis_triad:
            arrow_len = 0.9 * L
            los_scale = getattr(self, "los_arrow_scale", 1.35)
            self._clear_ref_quivers()
            for name, vec in [("North", (1, 0, 0)), ("East", (0, 1, 0)), ("LoS", (0, 0, 1))]:
                
                color = self._axis_colors.get(name, "gray")
                length = arrow_len * (los_scale if name == "LoS" else 1.0)
                self._ref_quivers.append(self.ax3d.quiver(0, 0, 0, *vec, length=length, arrow_length_ratio=0.07, lw=0.7, color=color, normalize=True)    
                                                     )
            self._arrow_len = arrow_len
            self._arrow_len_los = arrow_len * los_scale
        else:
            self._clear_ref_quivers()

        self._place_axis_labels()
        self._update_NE_guides()
        self._draw_corner_grid()