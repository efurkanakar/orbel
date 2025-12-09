"""Structural typing protocols describing what plotting mixins and helpers expect from their hosts."""

from __future__ import annotations

from typing import Any, Protocol


class DecorHostProtocol(Protocol):
    """Protocol describing what data OrbitDecorMixin needs from its host canvas."""
    ax3d: Any
    ax2d: Any
    canvas3d: Any
    sky_plane: Any

    _L: float
    _L_locked: float | None
    lock_axes_limits: bool
    _show_sky_plane: bool
    _show_sky_label: bool
    _sky_label_patch: Any | None
    _ne_lines: Any | None
    _show_ne_guides: bool
    _corner_lines: list[Any]
    _axis_texts: dict[str, Any]
    _axis_colors: dict[str, str]
    axis_label_xy_scale: float
    _arrow_len: float
    _arrow_len_los: float
    los_arrow_scale: float
    _show_axis_triad: bool
    _ref_quivers: list[Any]
    arc_eps: float

    def _update_w_arc(self) -> None: ...
    def _redraw(self) -> None: ...


class VisibilityHostProtocol(Protocol):
    """Protocol describing the attributes needed for visibility toggles."""
    asc3d: Any
    des3d: Any
    asc2d: Any
    des2d: Any
    nodes3d: Any
    nodes2d: Any
    Om_arc3d: Any
    w_arc3d: Any
    Om_arc2d: Any
    w_arc2d: Any
    i_wedge: Any
    sky_plane: Any
    _axis_texts: dict[str, Any]
    _body_artists: list[Any]
    _show_sky_plane: bool
    _show_sky_label: bool

    def _update_periastron(self) -> None: ...
    def _update_nodes(self) -> None: ...
    def _update_Om_arc(self) -> None: ...
    def _update_w_arc(self) -> None: ...
    def _update_i_wedge(self) -> None: ...
    def _update_sky_label_patch(self) -> None: ...
    def _clear_sky_label_patch(self) -> None: ...
    def _clear_ref_quivers(self) -> None: ...
    def _update_axes_limits(self) -> None: ...
    def _update_NE_guides(self) -> None: ...
    def _redraw(self) -> None: ...


class PeriLinkHostProtocol(VisibilityHostProtocol, Protocol):
    """Visibility protocol extension for canvases that render a periapsis link."""
    def set_peri_link_visible(self, visible: bool) -> None: ...

class AnimatorHostProtocol(Protocol):
    """Minimal surface area OrbitAnimator expects from its host canvas."""
    mass_params: Any
    a: float
    M: float

    def _dir_sign(self) -> float: ...
    def _recompute_from_M(self) -> None: ...
    def _update_body_only(self) -> None: ...
    def _redraw(self) -> None: ...