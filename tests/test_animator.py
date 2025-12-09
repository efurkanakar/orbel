"""Unit tests for the OrbitAnimator helper."""

from __future__ import annotations

import pytest

from orbel_app.plotting import animator


class FakeSignal:
    def __init__(self) -> None:
        self.callback = None

    def connect(self, callback) -> None:
        self.callback = callback


class FakeTimer:
    def __init__(self) -> None:
        self._interval = 0
        self._active = False
        self.timeout = FakeSignal()

    def setInterval(self, value: int) -> None:
        self._interval = value

    def interval(self) -> int:
        return self._interval

    def isActive(self) -> bool:
        return self._active

    def start(self) -> None:
        self._active = True

    def stop(self) -> None:
        self._active = False


class FakeMass:
    def __init__(self, mean_motion: float = 5.0) -> None:
        self.mean_motion_value = mean_motion
        self.calls: list[float] = []

    def mean_motion(self, a: float) -> float:
        self.calls.append(a)
        return self.mean_motion_value


class FakeHost:
    def __init__(self) -> None:
        self.mass_params = FakeMass()
        self.a = 2.0
        self.M = 0.0
        self._dir = 1.0
        self.recompute_called = 0
        self.update_body_calls = 0
        self.redraw_calls = 0

    def _dir_sign(self) -> float:
        return self._dir

    def _recompute_from_M(self) -> None:
        self.recompute_called += 1

    def _update_body_only(self) -> None:
        self.update_body_calls += 1

    def _redraw(self) -> None:
        self.redraw_calls += 1


@pytest.fixture(autouse=True)
def fake_qtimer(monkeypatch):
    monkeypatch.setattr(animator, "QTimer", FakeTimer)
    yield


def test_animator_start_and_stop_toggle_timer():
    host = FakeHost()
    anim = animator.OrbitAnimator(host)

    assert anim.timer.isActive() is False
    anim.start()
    assert anim.timer.isActive() is True
    anim.stop()
    assert anim.timer.isActive() is False


def test_animator_speed_scale_adjusts_dM():
    host = FakeHost()
    host.mass_params = FakeMass(mean_motion=4.0)
    anim = animator.OrbitAnimator(host)

    anim.set_speed_scale(2.0)

    expected = 4.0 * (anim.timer.interval() / 1000.0) * 2.0
    assert anim.dM == pytest.approx(expected)
    assert host.mass_params.calls[-1] == host.a


def test_animator_step_updates_host_state():
    host = FakeHost()
    anim = animator.OrbitAnimator(host)
    anim.dM = 0.1

    anim._step()

    assert host.M == pytest.approx(0.1)
    assert host.recompute_called == 1
    assert host.update_body_calls == 1
    assert host.redraw_calls == 1
