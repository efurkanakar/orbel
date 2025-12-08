"""Unit tests for the CanvasManager visibility and helper methods."""

from __future__ import annotations

from orbel_app.ui.canvas_manager import CanvasManager


class FakeCanvas:
    def __init__(self, *, font_size=10, start_nu=0.0, init=None, L=None) -> None:
        self.nodes_visible: list[bool] = []
        self.line_nodes_visible: list[bool] = []
        self.Omega_visible: list[bool] = []
        self.omega_visible: list[bool] = []
        self.inclination_visible: list[bool] = []
        self.sky_plane_visible: list[bool] = []
        self.axis_triad_visible: list[bool] = []
        self.centers_visible: list[bool] = []
        self.bodies_visible: list[bool] = []
        self.peri_link_visible: list[bool] = []

        self.font_size = font_size
        self.start_nu = start_nu
        self.init = init or {}
        self._L = L

    # Visibility API
    def set_nodes_visible(self, value: bool) -> None:
        self.nodes_visible.append(bool(value))

    def set_line_of_nodes_visible(self, value: bool) -> None:
        self.line_nodes_visible.append(bool(value))

    def set_Omega_visible(self, value: bool) -> None:
        self.Omega_visible.append(bool(value))

    def set_omega_visible(self, value: bool) -> None:
        self.omega_visible.append(bool(value))

    def set_inclination_visible(self, value: bool) -> None:
        self.inclination_visible.append(bool(value))

    def set_sky_plane_visible(self, value: bool) -> None:
        self.sky_plane_visible.append(bool(value))

    def set_reference_axes_visible(self, value: bool) -> None:
        self.axis_triad_visible.append(bool(value))

    def set_centers_visible(self, value: bool) -> None:
        self.centers_visible.append(bool(value))

    def set_bodies_visible(self, value: bool) -> None:
        self.bodies_visible.append(bool(value))

    def set_peri_link_visible(self, value: bool) -> None:
        self.peri_link_visible.append(bool(value))

    # Methods required by OrbitCanvas interface but not exercised deeply here.
    def apply_parameters(self, params, *, keep_phase: bool) -> None: ...

    def apply_masses(self, masses) -> None: ...

    def update_all(self) -> None: ...

    def recompute_mean_motion(self) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def lock_axes(self, lock: bool = True, L: float | None = None) -> None: ...

    def set_limits(self, L: float) -> None: ...

    def set_ticks(
        self,
        count2d: int | None = None,
        count3d: int | None = None,
        step2d: float | None = None,
        prune_ends: bool = True,
    ) -> None: ...

    def apply_font_size(self, size: int, *, redraw: bool = True) -> None: ...

    def set_arc_epsilon(self, eps: float) -> None: ...


def test_set_visibility_for_both_scopes_calls_both_canvases():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)

    manager.set_visibility("show_nodes", True)

    assert rel.nodes_visible == [True]
    assert abs_canvas.nodes_visible == [True]


def test_set_visibility_for_abs_only_key_targets_absolute_canvas():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)

    manager.set_visibility("show_peri_link", False)

    assert rel.peri_link_visible == []
    assert abs_canvas.peri_link_visible == [False]


def test_unknown_visibility_key_is_ignored():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)

    manager.set_visibility("does_not_exist", True)

    assert rel.nodes_visible == []
    assert abs_canvas.nodes_visible == []


def test_helper_methods_reflect_relative_and_absolute_canvas_state():
    rel = FakeCanvas(font_size=14, start_nu=0.5, init={"a": 2.0, "e": 0.3})
    abs_canvas = FakeCanvas(L=3.4)
    manager = CanvasManager(rel, abs_canvas)

    assert manager.get_plot_font_size() == 14
    assert manager.get_start_nu() == 0.5
    assert manager.get_initial_config() == {"a": 2.0, "e": 0.3}
    assert manager.get_abs_locked_length() == 3.4

