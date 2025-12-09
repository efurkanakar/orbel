"""Helper builders and specs for the orbit parameter and option panels in the main window."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox, 
                             QDoubleSpinBox, 
                             QFrame, 
                             QGridLayout, 
                             QGroupBox, 
                             QHBoxLayout, 
                             QLabel, 
                             QSizePolicy, 
                             QSlider, 
                             QWidget)

from .config import OrbelConfig

@dataclass(frozen=True)
class ParameterSpec:
    """Describes limits and defaults for a single parameter control."""
    key: str
    label_html: str
    minimum: float
    maximum: float
    step: float
    default: float
    decimals: int


@dataclass
class ParameterControl:
    """Holds the slider/spin widgets backing a single parameter input."""
    slider: QSlider
    spin: QDoubleSpinBox
    minimum: float
    step: float


def build_parameter_group(
    title: str,
    specs: Sequence[ParameterSpec],
    *,
    slider_length: int = 190,
    columns: int = 2,
    slider_height: int = 18,
    label_width: int = 60,
    tooltips: Dict[str, str] | None = None,
) -> Tuple[QGroupBox, Dict[str, ParameterControl]]:
    """
    Build a group box containing labelled slider+spin controls.

    Returns the group and a dict mapping the parameter key to a small helper
    object that stores the widgets plus metadata needed for conversions.
    """

    group = QGroupBox(title)
    grid = QGridLayout(group)
    grid.setContentsMargins(8, 5, 8, 5)
    grid.setHorizontalSpacing(8)
    grid.setVerticalSpacing(4)

    controls: Dict[str, ParameterControl] = {}
    for idx, spec in enumerate(specs):
        row_widget = QWidget()
        row_widget.setObjectName("paramRow")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(4, 4, 4, 4)
        row_layout.setSpacing(8)

        label = QLabel(spec.label_html)
        label.setTextFormat(Qt.RichText)
        font = label.font()
        font.setBold(True)
        font.setItalic(True)
        label.setFont(font)
        label.setFixedWidth(label_width)
        label.setContentsMargins(6, 0, 0, 0)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(int(round((spec.maximum - spec.minimum) / spec.step)))
        slider.setFixedHeight(slider_height)
        slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        slider_wrapper = QWidget()

        slider_layout = QHBoxLayout(slider_wrapper)
        slider_layout.setContentsMargins(0, 0, 0, 0)   # sağ pad'i kaldır
        slider_layout.setSpacing(0)
        slider_layout.addWidget(slider)
        slider_wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        slider_wrapper.setMinimumWidth(slider_length)  # min genişlik artık wrapper'da

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("color:gainsboro;")

        spin = QDoubleSpinBox()
        spin.setDecimals(spec.decimals)
        spin.setRange(spec.minimum, spec.maximum)
        spin.setSingleStep(spec.step)
        spin.setValue(spec.default)
        spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spin.setFixedWidth(70)

        slider.setValue(int(round((spec.default - spec.minimum) / spec.step)))

        tooltip = (tooltips or {}).get(spec.key)
        if tooltip:
            label.setToolTip(tooltip)
            slider.setToolTip(tooltip)
            spin.setToolTip(tooltip)

        row_layout.addWidget(label)
        row_layout.addWidget(slider_wrapper, 1)
        row_layout.addWidget(separator)
        row_layout.addWidget(spin, 0)

        row_layout.setStretch(0, 0)
        row_layout.setStretch(1, 1)
        row_layout.setStretch(2, 0)
        row_layout.setStretch(3, 0)

        row, col = divmod(idx, max(1, columns))
        grid.addWidget(row_widget, row, col)

        controls[spec.key] = ParameterControl(slider, spin, spec.minimum, spec.step)

    for col in range(max(1, columns)):
        grid.setColumnStretch(col, 1)
    return group, controls


@dataclass(frozen=True)
class OptionSpec:
    """Descriptor for a single checkbox option in the options panel."""
    key: str
    label: str
    tooltip: str | None = None
    checked: bool = True


def build_options_group(title: str, specs: Sequence[OptionSpec]) -> Tuple[QGroupBox, Dict[str, QCheckBox]]:
    """Return a two-column grid of checkboxes with rich-text labels."""

    group = QGroupBox(title)
    group.setObjectName("optionsCard")
    group.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    layout = QGridLayout(group)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setHorizontalSpacing(12)
    layout.setVerticalSpacing(4)

    checkboxes: Dict[str, QCheckBox] = {}
    for idx, spec in enumerate(specs):
        row = idx // 2
        col = idx % 2

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        checkbox = QCheckBox()
        checkbox.setChecked(spec.checked)

        label = QLabel(spec.label)
        label.setTextFormat(Qt.RichText)
        original_mouse_press = label.mousePressEvent

        def _label_mouse_press(event, cb=checkbox, orig=original_mouse_press):
            cb.toggle()
            if orig is not None:
                orig(event)

        label.mousePressEvent = _label_mouse_press

        if spec.tooltip:
            checkbox.setToolTip(spec.tooltip)
            label.setToolTip(spec.tooltip)

        row_layout.addWidget(checkbox, 0)
        row_layout.addWidget(label, 1)
        layout.addWidget(row_widget, row, col)

        checkboxes[spec.key] = checkbox

    return group, checkboxes

def make_size_parameters(cfg: OrbelConfig):

    return (ParameterSpec("a", "a", cfg.rel_a_min, cfg.rel_a_max, 0.01, cfg.rel_a_min, 2),
            ParameterSpec("e", "e", 0.0, 0.95, 0.01, 0.55, 2))


def make_orientation_parameters():
    
    return (ParameterSpec("i", "<i>i</i> (°)", 0.0, 180.0, 1.0, 40.0, 0),
            ParameterSpec("w", "&omega; (°)", 0.0, 360.0, 1.0, 60.0, 0),
            ParameterSpec("Om", "&Omega; (°)", 0.0, 360.0, 1.0, 25.0, 0))

def make_mass_parameters():

    return (ParameterSpec("m1", "m<sub>1</sub>", 0.1, 5.0, 0.1, 2.0, 1),
            ParameterSpec("m2", "m<sub>2</sub>", 0.1, 5.0, 0.1, 1.2, 1))


def tint_slider(control: "ParameterControl", color: str, groove_height: int = 6) -> None:
    slider = control.slider
    style = f"""
    QSlider::groove:horizontal {{
        height: {groove_height}px; background: gainsboro; border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {color}; border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        width: 14px; height: 14px; margin: -5px 0;
        border: 1px solid #111827; border-radius: 7px; background: #ffffff;
    }}
    QSlider::handle:horizontal:hover  {{ border: 1px solid #0f172a; }}
    QSlider::handle:horizontal:pressed {{ width: 16px; height: 16px; }}
    """
    slider.setStyleSheet(style)

def tint_parameter_sliders(ctrls: Dict[str, "ParameterControl"]) -> None:
    param_colors = {"a":  "purple",
                    "e":  "gold",
                    "m1": "red",
                    "m2": "mediumblue",
                    "i":  "cyan",
                    "w":  "darkorange",
                    "Om": "seagreen"}
    
    for key, color in param_colors.items():
        if key in ctrls:
            tint_slider(ctrls[key], color, groove_height=4)

__all__ = [
    "ParameterSpec","ParameterControl",
    "OptionSpec",
    "build_parameter_group","build_options_group",
    "make_size_parameters","make_orientation_parameters","make_mass_parameters",
    "tint_slider", "tint_parameter_sliders"
]