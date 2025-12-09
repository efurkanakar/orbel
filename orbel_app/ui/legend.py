"""Legend widgets that explain 3D markers."""

from __future__ import annotations

import numpy as np
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QWidget, QGroupBox, QGridLayout, QSizePolicy)


class LegendIcon(QWidget):
    """Paint a small pictogram matching orbit elements."""

    def __init__(self, kind: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.kind = kind
        self.setFixedSize(18, 18)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        colors = {"line": QColor("#cbd5e1"),
                  "gold": QColor("#facc15"),
                  "blue": QColor("dodgerblue"),
                  "red": QColor("firebrick"),
                  "gray": QColor("#9ca3af"),
                  "black": QColor("#000000")}

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.35

        if self.kind == "periastron":
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            painter.setPen(QPen(colors["line"], 1))
            painter.setBrush(QBrush(colors["gold"]))
            painter.drawPolygon(QPolygonF(QPointF(x, y) for x, y in pts))

        elif self.kind == "asc":
            pts = [(cx, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
            painter.setPen(QPen(colors["blue"], 1))
            painter.setBrush(QBrush(colors["blue"]))
            painter.drawPolygon(QPolygonF(QPointF(x, y) for x, y in pts))

        elif self.kind == "des":
            pts = [(cx - r, cy - r), (cx + r, cy - r), (cx, cy + r)]
            painter.setPen(QPen(colors["red"], 1))
            painter.setBrush(QBrush(colors["red"]))
            painter.drawPolygon(QPolygonF(QPointF(x, y) for x, y in pts))

        elif self.kind == "nodes":
            painter.setPen(QPen(colors["gray"], 2, Qt.DashLine))
            painter.drawLine(int(w * 0.15), int(cy), int(w * 0.85), int(cy))

        elif self.kind == "star":
            painter.translate(cx, cy)
            painter.setPen(QPen(colors["black"], 1.0))
            painter.setBrush(QBrush(colors["black"]))
            outer = r
            inner = r * 0.45
            pts = []
            for k in range(10):
                ang = -np.pi / 2 + k * np.pi / 5
                rad = outer if k % 2 == 0 else inner
                pts.append(QPointF(rad * np.cos(ang), rad * np.sin(ang)))
            painter.drawPolygon(QPolygonF(pts))

        elif self.kind == "bodies":
            painter.setPen(QPen(colors["line"], 1))
            painter.setBrush(QBrush(QColor("navy")))
            painter.drawEllipse(int(cx - 6), int(cy - 5), 10, 10)
            painter.setBrush(QBrush(QColor("darkred")))
            painter.drawEllipse(int(cx + 2), int(cy - 5), 10, 10)

        painter.end()


def legend_row(text: str, kind: str) -> QWidget:
    """Return a textual row plus icon for the legend box."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    icon = LegendIcon(kind)
    label = QLabel(text)
    label.setTextFormat(Qt.RichText)
    font = label.font()
    font.setPointSize(10)
    label.setFont(font)
    layout.addWidget(icon, 0)
    layout.addWidget(label, 1)
    return row

def create_legend_box() -> QGroupBox:
    legend_box = QGroupBox("Legend")
    legend_box.setObjectName("legendBox")
    legend_box.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    legend_items = [legend_row("Periastron", "periastron"),
                    legend_row("Central star", "star"),
                    legend_row("Ascending node", "asc"),
                    legend_row("Descending node", "des"),
                    legend_row("Nodes line", "nodes"),
                    legend_row("Bodies", "bodies")]
    
    legend_grid = QGridLayout(legend_box)
    legend_grid.setContentsMargins(6, 4, 6, 4)
    legend_grid.setHorizontalSpacing(10)
    legend_grid.setVerticalSpacing(4)
    for idx, widget in enumerate(legend_items):
        row = idx // 2
        col = idx % 2
        legend_grid.addWidget(widget, row, col)
        legend_grid.setColumnStretch(col, 1)
    for row in range(3):
        legend_grid.setRowStretch(row, 1)
    legend_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    return legend_box

__all__ = ["LegendIcon", "legend_row", "create_legend_box"]