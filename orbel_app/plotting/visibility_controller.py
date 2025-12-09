"""Controller object that handles visibility toggles for a canvas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

@dataclass(slots=True)
class VisibilityContext:
    """Wiring bundle that exposes artists and callbacks required for visibility toggles."""
    set_flag: Callable[[str, bool], None]
    get_flag: Callable[[str], bool]
    redraw: Callable[[], None]
    node_artists: Iterable
    line_node_artists: Iterable
    update_periastron: Callable[[], None]
    update_nodes: Callable[[], None]
    update_Om_arc: Callable[[], None]
    update_w_arc: Callable[[], None]
    update_i_wedge: Callable[[], None]
    update_sky_label: Callable[[], None]
    clear_sky_label: Callable[[], None]
    clear_ref_quivers: Callable[[], None]
    update_axes_limits: Callable[[], None]
    update_ne_guides: Callable[[], None]
    axis_texts: dict[str, Any]
    sky_plane: Any
    center3d: Any
    center2d: Any
    body_artists: Iterable

class VisibilityController:
    """Updates canvas visibility flags and associated artists as options change."""
    def __init__(self, context: VisibilityContext) -> None:
        self.ctx = context

    def _apply_flag(self, attr: str, value: bool) -> bool:
        state = bool(value)
        self.ctx.set_flag(attr, state)
        return state

    def set_nodes_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_nodes", visible)

        for art in ctx.node_artists:
            try:
                art.set_visible(bool(visible))
            except Exception:
                pass
        ctx.update_periastron()
        ctx.redraw()

    def set_line_of_nodes_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_line_nodes", visible)
        for art in ctx.line_node_artists:
            try:
                art.set_visible(bool(visible))
            except Exception:
                pass
        ctx.update_nodes()
        ctx.redraw()

    def set_Omega_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_Om", visible)
        ctx.update_Om_arc()
        ctx.redraw()

    def set_omega_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_omega", visible)
        ctx.update_w_arc()
        ctx.redraw()

    def set_inclination_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_i_wedge", visible)
        ctx.update_i_wedge()
        ctx.redraw()

    def set_skyplane_label_visible(self, visible: bool) -> None:
        ctx = self.ctx
        state = self._apply_flag("_show_sky_label", visible)
        if state and ctx.get_flag("_show_sky_plane"):
            ctx.update_sky_label()
        else:
            ctx.clear_sky_label()
        ctx.redraw()

    def set_sky_plane_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_sky_plane", visible)
        ctx.sky_plane.set_visible(bool(visible))
        if not visible:
            ctx.clear_sky_label()
        elif ctx.get_flag("_show_sky_label"):
            ctx.update_sky_label()
        ctx.redraw()

    def set_reference_axes_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_axis_triad", visible)
        if not visible:
            ctx.clear_ref_quivers()
            for lbl in ctx.axis_texts.values():
                lbl.set_visible(False)
        else:
            ctx.update_axes_limits()
        ctx.redraw()

    def set_ne_guides_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_ne_guides", visible)
        ctx.update_ne_guides()
        ctx.redraw()

    def set_centers_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_centers", visible)
        state = bool(visible)
        if ctx.center3d is not None:
            ctx.center3d.set_visible(state)
        if ctx.center2d is not None:
            ctx.center2d.set_visible(state)
        ctx.redraw()

    def set_bodies_visible(self, visible: bool) -> None:
        ctx = self.ctx
        self._apply_flag("_show_bodies", visible)
        for art in ctx.body_artists:
            try:
                art.set_visible(bool(visible))
            except Exception:
                pass
        ctx.redraw()