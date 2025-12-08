"""Composable builder for the parameter/option control panel, legend and playback controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox,
                             QGridLayout,
                             QGroupBox,
                             QHBoxLayout,
                             QVBoxLayout,
                             QWidget)

from .components import PlayerControls
from .legend import create_legend_box

from .panels import (ParameterControl,
                     build_options_group,
                     build_parameter_group,
                     make_mass_parameters,
                     make_orientation_parameters,
                     make_size_parameters)

from .config import OrbelConfig
from .constants import option_specs

@dataclass(slots=True)
class ControlPanelBundle:
    """Aggregate object exposing the assembled control panel widgets and hooks."""
    widget: QWidget
    controls: Dict[str, ParameterControl]
    option_checks: Dict[str, QCheckBox]
    player_controls: PlayerControls


def create_control_panel(config: OrbelConfig, tooltips, icon_provider: Callable[[str], object]) -> ControlPanelBundle:
    ctrl_panel = QWidget()
    ctrl_panel.setObjectName("ctrlPanel")
    ctrl_layout = QHBoxLayout(ctrl_panel)
    ctrl_layout.setContentsMargins(0, 0, 0, 0)
    ctrl_layout.setSpacing(6)

    params_group = QGroupBox("Orbit Parameters")
    params_group.setObjectName("paramsCard")
    params_group.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    params_layout = QVBoxLayout(params_group)
    params_layout.setContentsMargins(4, 4, 4, 4)
    params_layout.setSpacing(6)

    geom_specs = make_size_parameters(config)
    mass_specs = make_mass_parameters()
    orient_specs = make_orientation_parameters()

    ae_specs = geom_specs[:2]

    ae_box, ae_ctrls = build_parameter_group("Orbit Size",
                                             ae_specs,
                                             slider_length=180,
                                             columns=1,
                                             slider_height=14,
                                             label_width=60,
                                             tooltips=tooltips)

    masses_box, masses_ctrls = build_parameter_group("Masses",
                                                     mass_specs,
                                                     slider_length=180,
                                                     columns=1,
                                                     slider_height=14,
                                                     label_width=60,
                                                     tooltips=tooltips)

    orient_box, orient_ctrls = build_parameter_group("Orientation",
                                                     orient_specs,
                                                     slider_length=230,
                                                     columns=3,
                                                     slider_height=14,
                                                     label_width=58,
                                                     tooltips=tooltips)

    top_grid = QGridLayout()
    top_grid.setContentsMargins(0, 0, 0, 0)
    top_grid.setHorizontalSpacing(12)
    top_grid.setVerticalSpacing(6)

    left_col = QWidget()
    left_v = QVBoxLayout(left_col)
    left_v.setContentsMargins(0, 0, 0, 0)
    left_v.setSpacing(6)
    left_v.addWidget(ae_box)

    right_col = QWidget()
    right_v = QVBoxLayout(right_col)
    right_v.setContentsMargins(0, 0, 0, 0)
    right_v.setSpacing(6)
    right_v.addWidget(masses_box)

    top_grid.addWidget(left_col, 0, 0)
    top_grid.addWidget(right_col, 0, 1)

    params_layout.addLayout(top_grid)
    params_layout.addWidget(orient_box)

    options_group, option_checks = build_options_group("Options", option_specs)

    legend_column = QVBoxLayout()
    legend_column.setContentsMargins(0, 0, 0, 0)
    legend_column.setSpacing(4)

    controls = PlayerControls(icon_provider)
    legend_column.addWidget(create_legend_box(), 1)
    legend_column.addWidget(controls, 0)
    legend_host = QWidget()
    legend_host.setLayout(legend_column)

    ctrl_layout.addWidget(params_group, 2)
    ctrl_layout.addWidget(options_group, 1)
    ctrl_layout.addWidget(legend_host, 1)

    ctrl_bundle = ControlPanelBundle(widget=ctrl_panel,
                                     controls=dict(ae_ctrls | orient_ctrls | masses_ctrls),
                                     option_checks=option_checks,
                                     player_controls=controls)
    return ctrl_bundle