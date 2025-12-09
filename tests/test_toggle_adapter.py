"Tests for the visibility toggle adapter."

from unittest.mock import MagicMock

import pytest

from orbel_app.ui.canvas_manager import CanvasManager
from orbel_app.ui.toggle_adapter import ToggleAdapter


class FakeCanvas:
    def __init__(self) -> None:
        self.calls = []
        self.nodes_visible = []
        self.bodies_visible = []

    def set_peri_link_visible(self, value: bool) -> None:
        self.calls.append(value)

    # Minimal protocol surface needed for other toggles
    def set_nodes_visible(self, value: bool) -> None:
        self.nodes_visible.append(value)

    def set_line_of_nodes_visible(self, value: bool) -> None: ...

    def set_Omega_visible(self, value: bool) -> None: ...

    def set_omega_visible(self, value: bool) -> None: ...

    def set_inclination_visible(self, value: bool) -> None: ...

    def set_sky_plane_visible(self, value: bool) -> None: ...

    def set_reference_axes_visible(self, value: bool) -> None: ...

    def set_centers_visible(self, value: bool) -> None: ...

    def set_bodies_visible(self, value: bool) -> None:
        self.bodies_visible.append(value)

    def update_all(self) -> None: ...

    def recompute_mean_motion(self) -> None: ...

    def apply_parameters(self, params, *, keep_phase: bool) -> None: ...

    def apply_masses(self, masses) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...


def test_toggle_adapter_calls_peri_link_on_absolute_canvas():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)
    adapter = ToggleAdapter(manager)

    adapter.apply("show_peri_link", True)

    assert abs_canvas.calls == [True]
    assert rel.calls == []


def test_toggle_adapter_forwards_visibility_call():
    manager = MagicMock(spec=CanvasManager)
    adapter = ToggleAdapter(manager)

    adapter.apply("show_nodes", False)

    manager.set_visibility.assert_called_once_with("show_nodes", False)


def test_toggle_adapter_routes_visibility_to_both_canvases():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)
    adapter = ToggleAdapter(manager)

    adapter.apply("show_nodes", False)

    assert rel.nodes_visible == [False]
    assert abs_canvas.nodes_visible == [False]


def test_toggle_adapter_routes_bodies_visibility_to_both_canvases():
    rel = FakeCanvas()
    abs_canvas = FakeCanvas()
    manager = CanvasManager(rel, abs_canvas)
    adapter = ToggleAdapter(manager)

    adapter.apply("show_bodies", True)

    assert rel.bodies_visible == [True]
    assert abs_canvas.bodies_visible == [True]
