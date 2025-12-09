"""Builders for the stacked 3D/2D canvas area and its vertical view tabs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QButtonGroup,
                             QHBoxLayout,
                             QSizePolicy,
                             QStackedLayout,
                             QVBoxLayout,
                             QWidget)

from PyQt5.QtGui import QFont
from .components import VerticalButton

@dataclass(slots=True)
class DisplayAreaBundle:
    """Holds the assembled display widget plus the 3d/2d stacked layouts and tab buttons."""
    widget: QWidget
    stack_3d: QStackedLayout
    stack_2d: QStackedLayout
    tab_group: QButtonGroup
    tab_buttons: List[VerticalButton]

def create_display_area() -> DisplayAreaBundle:
    display_group = QWidget()
    display_group.setObjectName("displayGroup")
    display_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    display_layout = QHBoxLayout(display_group)
    display_layout.setContentsMargins(0, 0, 0, 0)
    display_layout.setSpacing(10)

    tab_column = QWidget()
    tab_column.setObjectName("tabColumn")
    tab_column.setFixedWidth(70)
    tab_column.setMinimumHeight(0)
    tab_column.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    tab_layout = QVBoxLayout(tab_column)
    tab_layout.setContentsMargins(4, 8, 4, 8)
    tab_layout.setSpacing(8)
    tab_layout.setAlignment(Qt.AlignTop)

    tab_buttons: List[VerticalButton] = []
    tab_button_group = QButtonGroup()
    font = QFont("Segoe UI", 12, QFont.DemiBold)
    font.setStyleStrategy(QFont.PreferAntialias | QFont.PreferQuality)
    for idx, title in enumerate(("Relative Orbit", "Absolute Orbit")):
        btn = VerticalButton(title)
        btn.setObjectName("tabButton")
        btn.setFont(font)
        btn.setCheckable(True)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tab_layout.addWidget(btn, 0)
        tab_buttons.append(btn)
        tab_button_group.addButton(btn, idx)

    tab_layout.addStretch(1)
    display_layout.addWidget(tab_column, 0)

    plot_holder = QWidget()
    plot_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    plot_holder_layout = QVBoxLayout(plot_holder)
    plot_holder_layout.setContentsMargins(0, 0, 0, 0)
    plot_holder_layout.setSpacing(8)

    gfx_row = QHBoxLayout()
    gfx_row.setContentsMargins(0, 0, 0, 0)
    gfx_row.setSpacing(10)
    plot_holder_layout.addLayout(gfx_row, 1)
    display_layout.addWidget(plot_holder, 1)

    mid_col = QWidget()
    mid_layout = QVBoxLayout(mid_col)
    mid_layout.setContentsMargins(0, 0, 0, 0)
    mid_layout.setSpacing(0)
    stack_3d = QStackedLayout()
    mid_layout.addLayout(stack_3d)

    right_col = QWidget()
    right_layout = QVBoxLayout(right_col)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)
    stack_2d = QStackedLayout()
    right_layout.addLayout(stack_2d)

    mid_col.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    right_col.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    gfx_row.addWidget(mid_col, 1)
    gfx_row.addWidget(right_col, 1)

    return DisplayAreaBundle(widget=display_group,
                             stack_3d=stack_3d,
                             stack_2d=stack_2d,
                             tab_group=tab_button_group,
                             tab_buttons=tab_buttons)
