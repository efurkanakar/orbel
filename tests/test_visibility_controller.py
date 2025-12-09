"""Unit tests for the standalone VisibilityController helper."""

from __future__ import annotations

from orbel_app.plotting.visibility_controller import VisibilityContext, VisibilityController


class DummyArtist:
    def __init__(self) -> None:
        self.visible = None

    def set_visible(self, value: bool) -> None:
        self.visible = value


def make_controller(initial_state: dict | None = None):
    state = {
        "_show_sky_plane": True,
        "_show_sky_label": True,
        "_show_axis_triad": True,
    }
    if initial_state:
        state.update(initial_state)

    calls = {
        "update_sky_label": 0,
        "clear_sky_label": 0,
        "clear_ref_quivers": 0,
        "update_axes_limits": 0,
        "update_ne_guides": 0,
        "redraw": 0,
    }

    axis_texts = {name: DummyArtist() for name in ("North", "East", "LoS")}

    def set_flag(name: str, value: bool) -> None:
        state[name] = bool(value)

    def get_flag(name: str) -> bool:
        return bool(state.get(name, False))

    def inc(name: str) -> None:
        calls[name] += 1

    context = VisibilityContext(
        set_flag=set_flag,
        get_flag=get_flag,
        redraw=lambda: inc("redraw"),
        node_artists=(DummyArtist(),),
        line_node_artists=(DummyArtist(),),
        update_periastron=lambda: None,
        update_nodes=lambda: None,
        update_Om_arc=lambda: None,
        update_w_arc=lambda: None,
        update_i_wedge=lambda: None,
        update_sky_label=lambda: inc("update_sky_label"),
        clear_sky_label=lambda: inc("clear_sky_label"),
        clear_ref_quivers=lambda: inc("clear_ref_quivers"),
        update_axes_limits=lambda: inc("update_axes_limits"),
        update_ne_guides=lambda: inc("update_ne_guides"),
        axis_texts=axis_texts,
        sky_plane=DummyArtist(),
        center3d=DummyArtist(),
        center2d=DummyArtist(),
        body_artists=(DummyArtist(),),
    )

    controller = VisibilityController(context)
    return controller, context, state, calls, axis_texts


def test_skyplane_label_visibility_updates_patch():
    controller, ctx, state, calls, _ = make_controller()

    controller.set_skyplane_label_visible(True)
    assert state["_show_sky_label"] is True
    assert calls["update_sky_label"] == 1
    assert calls["clear_sky_label"] == 0

    controller.set_skyplane_label_visible(False)
    assert state["_show_sky_label"] is False
    assert calls["clear_sky_label"] == 1


def test_sky_plane_visibility_updates_plane_artist():
    controller, ctx, state, calls, _ = make_controller()

    controller.set_sky_plane_visible(False)
    assert state["_show_sky_plane"] is False
    assert ctx.sky_plane.visible is False
    assert calls["clear_sky_label"] == 1

    controller.set_sky_plane_visible(True)
    assert ctx.sky_plane.visible is True
    assert calls["update_sky_label"] == 1


def test_reference_axes_toggle_clears_and_restores_guides():
    controller, ctx, state, calls, axis_texts = make_controller()

    controller.set_reference_axes_visible(False)
    assert calls["clear_ref_quivers"] == 1
    assert calls["update_axes_limits"] == 0
    assert all(artist.visible is False for artist in axis_texts.values())

    controller.set_reference_axes_visible(True)
    assert calls["update_axes_limits"] == 1
