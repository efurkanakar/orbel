"""Factory functions that construct all Matplotlib artists used by the orbit canvases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from mpl_toolkits.mplot3d.art3d import Poly3DCollection


@dataclass(slots=True)
class ArtistBundle:
    """Container for all Matplotlib artists used by a canvas."""
    center3d: Any
    center2d: Any
    axis_texts: Dict[str, Any]
    axis_colors: Dict[str, str]
    i_wedge: Poly3DCollection
    sky_plane: Poly3DCollection
    orbit3d: Any
    nodes3d: Any
    asc3d: Any
    des3d: Any
    peri3d: Any
    Om_arc3d: Any
    w_arc3d: Any
    body3d: Any
    orbit2d: Any
    nodes2d: Any
    asc2d: Any
    des2d: Any
    peri2d: Any
    Om_arc2d: Any
    w_arc2d: Any
    body2d: Any
    body_artists: list


def create_artists(ax3d, ax2d, font_size: int) -> ArtistBundle:
    center3d = ax3d.scatter(0, 0, 0, marker="*", c="black", s=80, zorder=8)
    center2d = ax2d.scatter(0, 0,    marker="*", c="black", s=80, zorder=6)

    axis_texts = {
        "North": ax3d.text2D(0, 0, "North", transform=ax3d.transAxes, fontsize=font_size, ha="center", va="center"),
        "East":  ax3d.text2D(0, 0, "East",  transform=ax3d.transAxes, fontsize=font_size, ha="center", va="center"),
        "LoS":   ax3d.text2D(0, 0, "LoS",   transform=ax3d.transAxes, fontsize=font_size, ha="center", va="center"),
    }
    axis_colors = {"North": "gray", "East": "gray", "LoS": "gray"}
    for name, txt in axis_texts.items():
        txt.set_color(axis_colors.get(name, "gray"))

    i_wedge = Poly3DCollection([], facecolor="cyan", alpha=0.30, edgecolor="none", zorder=4)
    ax3d.add_collection3d(i_wedge)

    sky_plane = Poly3DCollection([], facecolor="teal", alpha=0.06, edgecolor="none", zorder=1)
    ax3d.add_collection3d(sky_plane)

    orbit3d, = ax3d.plot([], [], [], "k",                      lw=1.5, zorder=2)
    nodes3d, = ax3d.plot([], [], [], "--", color="gray",       lw=1.5, zorder=3, alpha=0.8)
    asc3d, = ax3d.plot([], [], [],   "^",  color="dodgerblue", ms=8,   zorder=12)
    des3d, = ax3d.plot([], [], [],   "v",  color="firebrick",  ms=8,   zorder=12)
    peri3d, = ax3d.plot([], [], [],  "d",  color="gold",       ms=8,   zorder=12)
    Om_arc3d, = ax3d.plot([], [], [],      color="seagreen",   lw=1.8, zorder=9)
    w_arc3d, = ax3d.plot([], [], [],       color="darkorange", lw=2,   zorder=11)
    body3d = ax3d.scatter([], [], [],      color="purple",     s=32,   zorder=15)

    orbit2d, = ax2d.plot([], [], "k",                      lw=1.5, zorder=2)
    nodes2d, = ax2d.plot([], [], "--", color="gray",       lw=1.5, zorder=3, alpha=0.8)
    asc2d, = ax2d.plot([], [],   "^",  color="dodgerblue", ms=8,   zorder=12)
    des2d, = ax2d.plot([], [],   "v",  color="firebrick",  ms=8,   zorder=12)
    peri2d, = ax2d.plot([], [],  "d",  color="gold",       ms=8,   zorder=12)
    Om_arc2d, = ax2d.plot([], [],      color="seagreen",   lw=1.8, zorder=9)
    w_arc2d, = ax2d.plot([], [],       color="darkorange", lw=2,   zorder=11)
    body2d = ax2d.scatter([], [],      color="purple",     s=32,   zorder=15)

    body_artists = [body3d, body2d]

    return ArtistBundle(
        center3d=center3d,
        center2d=center2d,
        axis_texts=axis_texts,
        axis_colors=axis_colors,
        i_wedge=i_wedge,
        sky_plane=sky_plane,
        orbit3d=orbit3d,
        nodes3d=nodes3d,
        asc3d=asc3d,
        des3d=des3d,
        peri3d=peri3d,
        Om_arc3d=Om_arc3d,
        w_arc3d=w_arc3d,
        body3d=body3d,
        orbit2d=orbit2d,
        nodes2d=nodes2d,
        asc2d=asc2d,
        des2d=des2d,
        peri2d=peri2d,
        Om_arc2d=Om_arc2d,
        w_arc2d=w_arc2d,
        body2d=body2d,
        body_artists=body_artists,
    )