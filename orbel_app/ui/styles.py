"""Centralised Qt style sheets defining the overall look of the application."""

UI_QSS = """
QWidget { font-size: 13px; color: #111827; }

QWidget#mainRoot {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #fdfdfd, stop: 0.5 #f1f5f9, stop: 1 #e2e8f0);
    border-radius: 18px;
}
QWidget#ctrlPanel {
    background: transparent;
    border: none;
    padding: 6px;
}

QGroupBox {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    margin-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    top: -4px;
    padding: 0px 12px;
    color: #111827;
    font-weight: 500;
}

QGroupBox#paramsCard::title,
QGroupBox#optionsCard::title,
QGroupBox#legendBox::title,
QGroupBox#plotCard::title {
    subcontrol-position: top left;
    left: 8px;
    padding: 0px 12px;
}

 QGroupBox#paramsCard,
  QGroupBox#optionsCard,
  QGroupBox#legendBox,
  QGroupBox#plotCard {
    font-size: 13pt;
    font-weight: 500;
    margin-top: 10px;
}


QDoubleSpinBox { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px;
    padding: 4px 8px; min-height: 28px; min-width: 60px; }
QDoubleSpinBox:focus { border: 1px solid #111827; }


QPushButton#primaryBtn {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #1f2937, stop: 1 #0b1220);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    min-width: 96px;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #2c3648, stop: 1 #111827);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #0b1220, stop: 1 #050b16);
}

QPushButton#ghostBtn {
    background: rgba(248, 250, 252, 0.95);
    color: #111827;
    border: 1px solid #cbd5f5;
    border-radius: 8px;
    padding: 8px 14px;
    min-width: 96px;
    font-weight: 600;
}
QPushButton#ghostBtn:hover {
    background: #ecf2fb;
}
QPushButton#ghostBtn:pressed {
    background: #dce6f3;
}

#ctrlPanel QWidget#paramRow { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 6px 8px; }

QGroupBox#plotCard { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; }

QGroupBox#optionsCard,
QGroupBox#legendBox {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(226, 232, 240, 0.92);
}

QGroupBox#optionsCard QCheckBox {
    padding: 4px 6px;
    spacing: 8px;
    font-size: 12px;
    font-weight: 500;
}
QGroupBox#optionsCard QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 2px solid #cbd5e1;
    background: #ffffff;
    margin-right: 10px;
}
QGroupBox#optionsCard QCheckBox::indicator:hover {
    border-color: #111827;
}
QGroupBox#optionsCard QCheckBox::indicator:checked {
    border-color: #111827;
    background-color: #111827;
    image: url(:/qt-project.org/styles/commonstyle/images/check.png);
}
QGroupBox#optionsCard QCheckBox::indicator:disabled {
    border-color: #e5e7eb;
    background: #f3f4f6;
}

QWidget#displayGroup {
    background: transparent;
    border: none;
}

QWidget#tabColumn {
    background: #f5f7fb;
    border-radius: 18px 0 0 18px;
    min-height: 420px;
}

QPushButton#tabButton {
    background: transparent;
    color: #64748b;
    border: 1px solid rgba(148, 163, 184, 0.6);
    border-radius: 12px;
    padding: 10px 8px;
    margin-bottom: 6px;
    min-width: 1px;
    min-height: 48px;
    font-size: 14px;
    font-weight: 600;
    text-align: center;
}
QPushButton#tabButton[active="true"] {
    background: #ffffff;
    color: #0f172a;
    border-color: #9ca3af;
}

QPushButton#tabButton[active="false"]:hover {
    background: #ffffff;
    color: #0f172a;
    border-color: #8b98a8;
}

QPushButton#tabButton[active="true"]:hover {
    background: #ffffff;
    color: #0b1220;
    border-color: #7f8a99;
}

QPushButton#tabButton:pressed {
    background: #f2f4f8;
    border-color: #7c8796;
}


QPushButton#tabButton[active="false"] {
    background: transparent;
    color: #64748b;
}
QMenuBar {
    background-color: #f3f4f6;
    color: #111827;
    font-weight: 400;
}
QMenuBar::item {
    background: transparent;
    padding: 5px 12px;
}
QMenuBar::item:selected {
    background: #e5e7eb;
}
QMenu {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
}
QMenu::item:selected {
    background-color: #f3f4f6;
}
"""

SLIDER_QSS = """
QSlider::groove:horizontal { height: 6px; background: #e5e7eb; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #374151; border-radius: 3px; }
QSlider::handle:horizontal { width: 10px; height: 10px; margin: -3px 0;
    border: 1px solid #111827; border-radius: 5px; background: #ffffff; }
QSlider::handle:horizontal:hover { border: 1px solid #0f172a; }
QSlider::handle:horizontal:pressed { width: 12px; height: 12px; }
"""

__all__ = ["UI_QSS", "SLIDER_QSS"]