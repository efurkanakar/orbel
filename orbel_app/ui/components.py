"""Reusable Qt widget components for the orbel ui."""

from PyQt5.QtCore import QRect, QSize, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QPushButton, QStyle, QStyleOptionButton, QWidget, QHBoxLayout


class VerticalButton(QPushButton):
    """Push button that renders its label vertically."""

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        option = QStyleOptionButton()

        self.initStyleOption(option)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(-90)
        painter.translate(-self.height() / 2, -self.width() / 2)
        option.rect = QRect(0, 0, self.height(), self.width())

        self.style().drawControl(QStyle.CE_PushButton, option, painter, self)

    def sizeHint(self):
        s = super().sizeHint()
        return QSize(s.height(), s.width())

    def minimumSizeHint(self):
        s = super().minimumSizeHint()
        return QSize(s.height(), s.width())

    def set_visual_size(self, visual_width: int, visual_height: int):

        self.setSizePolicy(self.sizePolicy().Fixed, self.sizePolicy().Fixed)
        self.setMinimumSize(visual_height, visual_width)
        self.setMaximumSize(visual_height, visual_width)


class PlayerControls(QWidget):
    """Compact play/pause and reset control strip for orbit animation."""
    playToggled = pyqtSignal(bool)
    resetClicked = pyqtSignal()

    def __init__(self, icon_provider):
        super().__init__()
        self._icon = icon_provider
        self._playing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.btn_play = QPushButton(" Play")
        self.btn_play.setObjectName("primaryBtn")
        self.btn_play.setIcon(self._icon("play.ico"))
        self.btn_play.clicked.connect(self._on_play_clicked)

        self.btn_reset = QPushButton(" Reset")
        self.btn_reset.setObjectName("ghostBtn")
        self.btn_reset.setIcon(self._icon("reset.ico"))
        self.btn_reset.clicked.connect(self.resetClicked.emit)

        layout.addWidget(self.btn_play, 1)
        layout.addWidget(self.btn_reset, 1)

    def setPlaying(self, playing: bool) -> None:
        self._playing = bool(playing)

        if self._playing:
            self.btn_play.setText(" Pause")
            self.btn_play.setIcon(self._icon("pause.ico"))
        else:
            self.btn_play.setText(" Play")
            self.btn_play.setIcon(self._icon("play.ico"))

    def _on_play_clicked(self):

        self.playToggled.emit(not self._playing)

__all__ = ["VerticalButton", "PlayerControls"]