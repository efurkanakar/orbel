"""Animation helper that advances the orbit in time using a Qt timer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer

from .protocols import AnimatorHostProtocol


class OrbitAnimator:
    """Encapsulates timer-based animation logic for an orbit canvas."""

    def __init__(self, host: AnimatorHostProtocol, interval_ms: int = 15) -> None:
        self._host = host
        self.timer = QTimer()
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._step)
        self._speed_scale = 1.0
        self.dM = 0.020

    def start(self) -> None:
        if not self.timer.isActive():
            self.timer.start()

    def stop(self) -> None:
        if self.timer.isActive():
            self.timer.stop()

    def set_speed_scale(self, scale: float) -> None:
        self._speed_scale = max(float(scale), 0.0)
        self.recompute_mean_motion()

    def recompute_mean_motion(self) -> None:
        dt = max(self.timer.interval(), 1) / 1000.0
        mean_motion = self._host.mass_params.mean_motion(self._host.a)
        self.dM = mean_motion * dt * self._speed_scale

    def _step(self) -> None:
        self._host.M += self._host._dir_sign() * self.dM
        self._host._recompute_from_M()
        self._host._update_body_only()
        self._host._redraw()