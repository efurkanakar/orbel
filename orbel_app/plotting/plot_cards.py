"""Helpers for building the shared 3D/2D plot cards."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGroupBox, QSizePolicy, QVBoxLayout

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


@dataclass(slots=True)
class PlotCards:
    """Bundled Qt widgets and axes for the 3D and 2D plot cards."""
    card3d: QGroupBox
    card2d: QGroupBox
    ax3d: any
    ax2d: any
    canvas3d: FigureCanvas
    canvas2d: FigureCanvas
    toolbar3d: NavigationToolbar
    toolbar2d: NavigationToolbar


def create_plot_cards(title3d: str, title2d: str, font_size: int) -> PlotCards:
    plt.rcParams.update({
        "font.size": font_size,
        "axes.titlesize": font_size + 1,
        "axes.labelsize": font_size,
        "xtick.labelsize": max(8, font_size - 1),
        "ytick.labelsize": max(8, font_size - 1),
    })

    card3d = QGroupBox(title3d)
    card3d.setObjectName("plotCard")
    card3d.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    lay3d = QVBoxLayout(card3d)
    lay3d.setContentsMargins(8, 8, 8, 6)
    lay3d.setSpacing(6)

    fig3d = Figure(dpi=96)
    canvas3d = FigureCanvas(fig3d)
    canvas3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    card3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    lay3d.addWidget(canvas3d, 1)

    toolbar3d = NavigationToolbar(canvas3d, card3d)
    toolbar3d.setIconSize(QSize(28, 28))
    lay3d.addWidget(toolbar3d, 0)
    ax3d = fig3d.add_subplot(111, projection="3d")

    card2d = QGroupBox(title2d)
    card2d.setObjectName("plotCard")
    card2d.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    lay2d = QVBoxLayout(card2d)
    lay2d.setContentsMargins(8, 8, 8, 6)
    lay2d.setSpacing(6)

    fig2d = Figure(dpi=96)
    canvas2d = FigureCanvas(fig2d)
    canvas2d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    card2d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    lay2d.addWidget(canvas2d, 1)

    toolbar2d = NavigationToolbar(canvas2d, card2d)
    toolbar2d.setIconSize(QSize(28, 28))
    lay2d.addWidget(toolbar2d, 0)
    ax2d = fig2d.add_subplot(111)

    return PlotCards(card3d=card3d,
                     card2d=card2d,
                     ax3d=ax3d,
                     ax2d=ax2d,
                     canvas3d=canvas3d,
                     canvas2d=canvas2d,
                     toolbar3d=toolbar3d,
                     toolbar2d=toolbar2d)