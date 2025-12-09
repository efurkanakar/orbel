"""Qt main window for the orbel application."""

from PyQt5.QtWidgets import (QAction, QMainWindow, QMessageBox, QVBoxLayout, QWidget)

from ..plotting.models import MassParameters, OrbitParameters

from .styles import SLIDER_QSS, UI_QSS
from .config import OrbelConfig, DEFAULT_CONFIG
from .resources import load_icon
from .constants import parameter_tooltips, option_specs
from .panels import tint_parameter_sliders
from .canvas_manager import CanvasManager
from .control_panel import create_control_panel
from .display_area import create_display_area
from .option_controller import OptionController
from .parameter_controller import ParameterController
from .orbit_state import OrbitStateAdapter
from .toggle_adapter import ToggleAdapter


class MainWindow(QMainWindow):
    """Top-level Qt window that hosts the control panel and orbit canvases."""

    param_tooltips = parameter_tooltips

    def __init__(self, config: OrbelConfig = DEFAULT_CONFIG):
        super().__init__()
        self.config = config
        self.param_ctrl: ParameterController | None = None
        self._abs_axes_lock_L: float | None = None
        self.canvas_manager = CanvasManager()
        self.toggle_adapter = ToggleAdapter(self.canvas_manager)
        self.option_controller = OptionController(option_specs)

        self._setup_window_chrome()

        root = QWidget(self)
        root.setObjectName("mainRoot")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(8)

        ctrl_bundle = create_control_panel(self.config, self.param_tooltips, load_icon)
        outer.addWidget(ctrl_bundle.widget, 0)
        tint_parameter_sliders(ctrl_bundle.controls)
        self.param_ctrl = ParameterController(ctrl_bundle.controls)
        self.state_adapter = OrbitStateAdapter(self.param_ctrl)
        self.option_controller.register_checkboxes(ctrl_bundle.option_checks)
        self.controls = ctrl_bundle.player_controls

        display_bundle = create_display_area()
        outer.addWidget(display_bundle.widget, 1)
        self.stack_3d = display_bundle.stack_3d
        self.stack_2d = display_bundle.stack_2d
        self.tab_button_group = display_bundle.tab_group
        self.tab_buttons = display_bundle.tab_buttons
        self.tab_button_group.buttonClicked[int].connect(self._on_tab_changed)

        self.option_controller.attach_adapter(self.toggle_adapter)

        self._abs_axes_lock_L = self.canvas_manager.get_abs_locked_length()

        self.canvas_manager.add_cards_to_stacks(self.stack_3d, self.stack_2d)

        self._init_canvas_defaults()

        self._bind_parameter_controls()

        self.controls.playToggled.connect(self._on_play_toggled)
        self.controls.resetClicked.connect(self.reset_view)

        self._on_tab_changed(0)

        self.apply_params_from_init()
        self.option_controller.apply_all()

    def _update_all(self):
        if self.canvas_manager:
            self.canvas_manager.update_all()

    def _recompute_all(self):
        if self.canvas_manager:
            self.canvas_manager.recompute_all()

    def _setup_window_chrome(self) -> None:
        self.setWindowTitle("orbel")
        self.setWindowIcon(load_icon("orbel.ico"))
        self.setStyleSheet(UI_QSS + SLIDER_QSS)
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _bind_parameter_controls(self) -> None:
        if not self.param_ctrl:
            return
        keep_phase_cb = self.on_params_changed_keep_phase
        self.param_ctrl.bind("a", self.on_a_changed)
        for key in ("e", "i", "w", "Om"):
            self.param_ctrl.bind(key, keep_phase_cb)
        for key in ("m1", "m2"):
            self.param_ctrl.bind(key, self.on_mass_changed)

    def on_a_changed(self) -> None:
        params = self._orbit_params_from_controls()
        self._apply_canvas_parameters(params, keep_phase=True)

    def _init_canvas_defaults(self) -> None:
        self.canvas_manager.set_arc_epsilon(0.0)
        self.plot_font_size = self.canvas_manager.get_plot_font_size()

    def _orbit_params_from_controls(self, *, start_override: float | None = None) -> OrbitParameters:
        adapter = getattr(self, "state_adapter", None)
        if not adapter:
            return OrbitParameters(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        start_nu = start_override if start_override is not None else self.canvas_manager.get_start_nu()
        return adapter.read_orbit_params(start_nu=start_nu)

    def _mass_params_from_controls(self) -> MassParameters:
        adapter = getattr(self, "state_adapter", None)
        if not adapter:
            return MassParameters(0.0, 0.0)
        return adapter.read_masses()

    def _apply_canvas_parameters(self, params: OrbitParameters, *, keep_phase: bool) -> None:
        if not self.canvas_manager:
            return
        self.canvas_manager.apply_parameters(params, keep_phase=keep_phase)

    def _apply_canvas_masses(self, masses: MassParameters) -> None:
        if not self.canvas_manager:
            return
        self.canvas_manager.apply_masses(masses)

    def on_params_changed_keep_phase(self) -> None:
        params = self._orbit_params_from_controls()
        self._apply_canvas_parameters(params, keep_phase=True)

    def on_mass_changed(self) -> None:
        masses = self._mass_params_from_controls()
        self._apply_canvas_masses(masses)

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "About orbel",
            (
                "<b>orbel</b><br><br>"
                "I developed orbel to better understand orbital elements and to visualise relative and absolute "
                "Keplerian orbits in 3D and 2D.<br><br>"
                "During my master's thesis work on astrometry it started as a small exploration tool and later "
                "grew into a complete program.<br><br>"
                "If you have ideas or suggestions for improving orbel, please contact me:<br>"
                '<a href="mailto:efurkanakar@gmail.com">efurkanakar@gmail.com</a><br><br>'
            ),
        )

    def apply_params_from_init(self) -> None:
        init = self.canvas_manager.get_initial_config()
        a0 = init.get("a", self.config.rel_a_min)
        e = init["e"]
        i = init["i"]
        w = init["w"]
        Om = init["Om"]
        m1, m2 = init["m1"], init["m2"]
        start_nu = init["start_nu"]

        seed_params = OrbitParameters(a=a0, e=e, i=i, w=w, Om=Om, start_nu=start_nu)
        seed_masses = MassParameters(m1=m1, m2=m2)

        if self.state_adapter:
            self.state_adapter.write_orbit_params(seed_params)
            self.state_adapter.write_masses(seed_masses)
            params = self._orbit_params_from_controls(start_override=start_nu)
            masses = self._mass_params_from_controls()
        else:
            params = seed_params
            masses = seed_masses

        self._apply_canvas_parameters(params, keep_phase=False)
        self._apply_canvas_masses(masses)

        self.canvas_manager.lock_axes("rel", True)
        if self._abs_axes_lock_L is not None:
            self.canvas_manager.lock_axes("abs", True, self._abs_axes_lock_L)
        else:
            self.canvas_manager.lock_axes("abs", True)

        self.canvas_manager.set_limits(rel=3.3, abs=2.4)
        self.canvas_manager.set_ticks(
            rel={"count2d": 7, "count3d": 7, "prune_ends": True},
            abs={"count2d": 7, "count3d": 7, "prune_ends": True},
        )

        self.canvas_manager.apply_font_size(self.plot_font_size)

        self.option_controller.apply_all()


    def _on_play_toggled(self, play: bool) -> None:
        if self.canvas_manager:
            if play:
                self.canvas_manager.start()
            else:
                self.canvas_manager.stop()
        self.controls.setPlaying(play)

    def reset_view(self) -> None:
        if self.canvas_manager:
            self.canvas_manager.stop()
        self.controls.setPlaying(False)
        self.apply_params_from_init()

    def _on_tab_changed(self, idx: int) -> None:
        self.stack_3d.setCurrentIndex(idx)
        self.stack_2d.setCurrentIndex(idx)
        button = self.tab_button_group.button(idx)
        if button:
            button.setChecked(True)
        self._update_tab_styles()

    def _update_tab_styles(self) -> None:
        if not hasattr(self, "stack_3d") or not hasattr(self, "stack_2d"):
            return
        current = self.stack_3d.currentIndex()
        for index, btn in enumerate(self.tab_buttons):
            is_active = index == current
            btn.setProperty("active", is_active)
            btn.setChecked(is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

__all__ = ["MainWindow"]