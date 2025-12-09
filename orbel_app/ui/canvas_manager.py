"""Facade around the concrete canvases to decouple the UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Literal, Tuple, cast

from ..plotting import RelativeCanvas, AbsoluteCanvas
from ..plotting.interfaces import OrbitCanvas
from ..plotting.models import MassParameters, OrbitParameters
from ..plotting.protocols import VisibilityHostProtocol, PeriLinkHostProtocol

VisibilityFn = Callable[[VisibilityHostProtocol, bool], None]


def _set_nodes(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_nodes_visible(value)


def _set_line_nodes(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_line_of_nodes_visible(value)


def _set_Omega(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_Omega_visible(value)


def _set_omega(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_omega_visible(value)


def _set_inclination(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_inclination_visible(value)


def _set_sky_plane(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_sky_plane_visible(value)


def _set_axis_triad(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_reference_axes_visible(value)


def _set_centers(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_centers_visible(value)


def _set_bodies(canvas: VisibilityHostProtocol, value: bool) -> None:
    canvas.set_bodies_visible(value)


def _set_peri_link(canvas: VisibilityHostProtocol, value: bool) -> None:
    cast(PeriLinkHostProtocol, canvas).set_peri_link_visible(value)


@dataclass(frozen=True)
class VisibilityBinding:
    """Maps a toggle key to its handler and target scope (relative/absolute/both)."""
    scope: Literal["both", "rel", "abs"]
    handler: VisibilityFn


VISIBILITY_BINDINGS: Dict[str, VisibilityBinding] = {
    "show_nodes": VisibilityBinding("both", _set_nodes),
    "show_line_nodes": VisibilityBinding("both", _set_line_nodes),
    "show_Omega": VisibilityBinding("both", _set_Omega),
    "show_omega": VisibilityBinding("both", _set_omega),
    "show_inclination": VisibilityBinding("both", _set_inclination),
    "show_sky_plane": VisibilityBinding("both", _set_sky_plane),
    "show_axis_triad": VisibilityBinding("both", _set_axis_triad),
    "show_centers": VisibilityBinding("both", _set_centers),
    "show_bodies": VisibilityBinding("both", _set_bodies),
    "show_peri_link": VisibilityBinding("abs", _set_peri_link),
}


class CanvasManager:
    """Provides high-level operations and coordination for the relative and absolute canvases."""

    def __init__(self, relative: OrbitCanvas | None = None, absolute: OrbitCanvas | None = None) -> None:
        self._relative = relative or RelativeCanvas()
        self._absolute = absolute or AbsoluteCanvas()

    def iter_canvases(self) -> Iterable[OrbitCanvas]:
        yield self._relative
        yield self._absolute

    def apply_parameters(self, params: OrbitParameters, *, keep_phase: bool) -> None:
        for canvas in self.iter_canvases():
            canvas.apply_parameters(params, keep_phase=keep_phase)

    def apply_masses(self, masses: MassParameters) -> None:
        for canvas in self.iter_canvases():
            canvas.apply_masses(masses)

    def update_all(self) -> None:
        for canvas in self.iter_canvases():
            canvas.update_all()

    def recompute_all(self) -> None:
        for canvas in self.iter_canvases():
            canvas.recompute_mean_motion()

    def start(self) -> None:
        for canvas in self.iter_canvases():
            canvas.start()

    def stop(self) -> None:
        for canvas in self.iter_canvases():
            canvas.stop()

    def add_cards_to_stacks(self, stack3d, stack2d) -> None:
        stack3d.addWidget(self._relative.card3d)
        stack3d.addWidget(self._absolute.card3d)
        stack2d.addWidget(self._relative.card2d)
        stack2d.addWidget(self._absolute.card2d)

    def set_arc_epsilon(self, value: float, scope: str = "both") -> None:
        for canvas in self._targets(scope):
            canvas.set_arc_epsilon(value)

    def get_plot_font_size(self) -> int:
        return int(self._relative.font_size)

    def get_start_nu(self) -> float:
        return float(getattr(self._relative, "start_nu", 0.0))

    def get_initial_config(self) -> Dict[str, float]:
        return dict(self._relative.init)

    def get_abs_locked_length(self) -> float | None:
        abs_L = getattr(self._absolute, "_L", None)
        return float(abs_L) if abs_L is not None else None

    def lock_axes(self, scope: str, lock: bool = True, L: float | None = None) -> None:
        for canvas in self._targets(scope):
            canvas.lock_axes(lock, L)

    def set_limits(self, rel: float | None = None, abs: float | None = None) -> None:
        if rel is not None:
            self._relative.set_limits(rel)
        if abs is not None:
            self._absolute.set_limits(abs)

    def set_ticks(self, *, rel: Dict | None = None, abs: Dict | None = None) -> None:
        if rel:
            self._relative.set_ticks(**rel)
        if abs:
            self._absolute.set_ticks(**abs)

    def apply_font_size(self, size: int) -> None:
        self._relative.apply_font_size(size, redraw=False)
        self._absolute.apply_font_size(size, redraw=False)
        self._relative._redraw()
        self._absolute._redraw()

    def set_visibility(self, key: str, value: bool) -> None:
        binding = VISIBILITY_BINDINGS.get(key)
        if not binding:
            return
        for canvas in self._targets(binding.scope, key):
            binding.handler(canvas, value)

    def _targets(self, scope: str, key: str | None = None) -> Tuple[VisibilityHostProtocol, ...]:
        if scope == "rel":
            return (cast(VisibilityHostProtocol, self._relative),)
        if scope == "abs":
            target = self._absolute
            if key == "show_peri_link":
                return (cast(PeriLinkHostProtocol, target),)
            return (cast(VisibilityHostProtocol, target),)
        return (
            cast(VisibilityHostProtocol, self._relative),
            cast(VisibilityHostProtocol, self._absolute),
        )