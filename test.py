# PAT_Layout.py — Stage 1: Pure layout skeleton
# No data, no logic, no timers. Just the grid.

import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSlider,
    QFrame, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
FONT_PATH  = os.path.join(ASSETS_DIR, "Orbitron-VariableFont_wght.ttf")

# ──────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────
C_DARK   = "#212b58"   # navy — primary brand colour
C_PANEL  = "#f0f2f7"   # off-white panel background
C_CARD   = "#ffffff"   # white card background
C_BG     = "#e8ecf5"   # page background
C_GREEN  = "#00ff6a"   # accent green
C_BORDER = "#d0d5e8"   # subtle border

# ──────────────────────────────────────────────
# Shared style strings
# ──────────────────────────────────────────────
COMBO_STYLE = (
    "QComboBox { color: white; background-color: #212b58; "
    "border-radius: 5px; padding: 3px 8px; font-size: 10px; } "
    "QComboBox QAbstractItemView { background: #212b58; color: white; }"
)

BTN_DARK = (
    "QPushButton { background-color: #3a4a7a; color: white; "
    "border-radius: 5px; padding: 4px 12px; font-size: 11px; } "
    "QPushButton:hover { background-color: #4a5a9a; }"
)

BTN_PLAY = (
    "QPushButton { background-color: #1a6e3a; color: white; "
    "border-radius: 5px; padding: 4px 18px; font-size: 11px; font-weight: bold; } "
    "QPushButton:hover { background-color: #228b4a; }"
)

# ──────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────
def section_label(text, ff):
    """Dark navy pill label used as a sub-section header."""
    lbl = QLabel(text)
    lbl.setFont(QFont(ff, 8, QFont.Weight.Bold))
    lbl.setFixedHeight(20)
    lbl.setStyleSheet(
        f"color: white; background-color: {C_DARK}; "
        f"border-radius: 4px; padding: 1px 8px;"
    )
    return lbl


def placeholder(text, min_h=0):
    """Grey dashed placeholder box for panels not yet implemented."""
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background-color: {C_PANEL}; color: #8892b0; "
        f"border: 1px dashed {C_BORDER}; border-radius: 6px; "
        f"font-size: 11px;"
    )
    lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    if min_h:
        lbl.setMinimumHeight(min_h)
    return lbl


def h_divider():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {C_BORDER};")
    line.setFixedHeight(2)
    return line


def card(layout):
    """Wrap a QLayout in a white rounded card widget."""
    w = QWidget()
    w.setLayout(layout)
    w.setStyleSheet(
        f"background-color: {C_CARD}; border-radius: 10px;"
    )
    return w


# ──────────────────────────────────────────────
# Column builders
# ──────────────────────────────────────────────
def build_left_column(ff):
    """
    Left column — two stacked 2-D plot panels, each with a
    variable-selector dropdown above it.
    """
    col = QVBoxLayout()
    col.setSpacing(6)
    col.setContentsMargins(8, 8, 8, 8)

    # ── Top plot ──
    col.addWidget(section_label("Top Plot Variable", ff))
    top_combo = QComboBox()
    top_combo.addItems(["bmpAltitude", "gpsAltitude", "gpsSpeed",
                        "accelX", "accelY", "accelZ",
                        "gyroX", "gyroY", "gyroZ",
                        "magX", "magY", "magZ",
                        "imuTemp", "bmpTemp", "bmpPressure"])
    top_combo.setStyleSheet(COMBO_STYLE)
    col.addWidget(top_combo)
    col.addWidget(placeholder("📈  2-D Plot\n(Top)", min_h=80), stretch=1)

    col.addWidget(h_divider())

    # ── Bottom plot ──
    col.addWidget(section_label("Bottom Plot Variable", ff))
    bot_combo = QComboBox()
    bot_combo.addItems(["gpsSpeed", "bmpAltitude", "gpsAltitude",
                        "accelX", "accelY", "accelZ",
                        "gyroX", "gyroY", "gyroZ",
                        "magX", "magY", "magZ",
                        "imuTemp", "bmpTemp", "bmpPressure"])
    bot_combo.setStyleSheet(COMBO_STYLE)
    col.addWidget(bot_combo)
    col.addWidget(placeholder("📈  2-D Plot\n(Bottom)", min_h=80), stretch=1)

    return col


def build_middle_column(ff):
    """
    Middle column — 3-D trajectory visualiser on top,
    map panel on the bottom.
    """
    col = QVBoxLayout()
    col.setSpacing(6)
    col.setContentsMargins(8, 8, 8, 8)

    # ── 3-D visualiser ──
    col.addWidget(section_label("3-D Visualiser", ff))
    vis_combo = QComboBox()
    vis_combo.addItems(["GPS 3-D Trajectory"])
    vis_combo.setStyleSheet(COMBO_STYLE)
    col.addWidget(vis_combo)
    col.addWidget(placeholder("🌐  3-D Trajectory Plot", min_h=80), stretch=1)

    col.addWidget(h_divider())

    # ── Map ──
    col.addWidget(section_label("Map", ff))
    col.addWidget(placeholder("🗺  Map View\n(Coming soon)", min_h=80), stretch=1)

    return col


def build_right_column(ff):
    """
    Right column — camera feed (large, split CV / Raw) on top,
    avionics status grid on the bottom.
    """
    col = QVBoxLayout()
    col.setSpacing(6)
    col.setContentsMargins(8, 8, 8, 8)

    # ── Camera feed (split) ──
    col.addWidget(section_label("Camera Feed", ff))

    cam_row = QHBoxLayout()
    cam_row.setSpacing(4)
    cam_row.addWidget(placeholder("📷  Computer Vision Feed", min_h=60))
    cam_row.addWidget(placeholder("🎥  Raw Camera Feed",      min_h=60))
    cam_widget = QWidget()
    cam_widget.setLayout(cam_row)
    cam_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    col.addWidget(cam_widget, stretch=3)   # camera takes ~75 % of right col

    col.addWidget(h_divider())

    # ── Avionics status grid ──
    col.addWidget(section_label("Avionics Status", ff))

    AVIONICS_FIELDS = [
        ("GPS Fix",      "---"),  ("GPS Valid",    "---"),
        ("GPS Speed",    "---"),  ("GPS Heading",  "---"),
        ("Accel X",      "---"),  ("Accel Y",      "---"),
        ("Accel Z",      "---"),  ("Gyro X",       "---"),
        ("Gyro Y",       "---"),  ("Gyro Z",       "---"),
        ("Mag X",        "---"),  ("Mag Y",        "---"),
        ("Mag Z",        "---"),  ("IMU Temp",     "---"),
        ("BMP Temp",     "---"),  ("BMP Pressure", "---"),
    ]

    avi_grid = QGridLayout()
    avi_grid.setSpacing(3)
    avi_grid.setContentsMargins(4, 4, 4, 4)

    for i, (name, val) in enumerate(AVIONICS_FIELDS):
        row, col_offset = divmod(i, 2)
        name_lbl = QLabel(f"{name}:")
        name_lbl.setFont(QFont(ff, 8, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {C_DARK};")

        val_lbl = QLabel(val)
        val_lbl.setFont(QFont(ff, 8))
        val_lbl.setStyleSheet("color: #555;")
        val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        base = col_offset * 2
        avi_grid.addWidget(name_lbl, row, base)
        avi_grid.addWidget(val_lbl,  row, base + 1)

    avi_widget = QWidget()
    avi_widget.setLayout(avi_grid)
    avi_widget.setStyleSheet(
        f"background-color: {C_PANEL}; border-radius: 6px;"
    )
    avi_widget.setMaximumHeight(260)
    avi_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    col.addWidget(avi_widget, stretch=1)

    return col


def build_playback_bar(ff):
    """
    Bottom playback bar — load buttons, play/pause, restart,
    speed selector, scrub slider, time readout.
    """
    bar = QWidget()
    bar.setFixedHeight(48)
    bar.setStyleSheet(f"background-color: {C_DARK}; border-radius: 8px;")

    layout = QHBoxLayout(bar)
    layout.setContentsMargins(12, 6, 12, 6)
    layout.setSpacing(8)

    def dark_btn(text):
        b = QPushButton(text)
        b.setStyleSheet(BTN_DARK)
        b.setFont(QFont(ff, 9))
        return b

    btn_csv = dark_btn("📂 CSV")
    btn_cv  = dark_btn("📷 CV Video")
    btn_raw = dark_btn("🎥 Raw Video")
    btn_rst = dark_btn("↺ Restart")

    btn_play = QPushButton("▶  Play")
    btn_play.setStyleSheet(BTN_PLAY)
    btn_play.setFont(QFont(ff, 9, QFont.Weight.Bold))

    speed_lbl = QLabel("Speed:")
    speed_lbl.setStyleSheet("color: white; font-size: 10px;")
    speed_lbl.setFont(QFont(ff, 9))

    speed_combo = QComboBox()
    speed_combo.addItems(["0.25×", "0.5×", "1×", "2×", "5×", "10×"])
    speed_combo.setCurrentIndex(2)
    speed_combo.setStyleSheet(
        "QComboBox { background-color: #3a4a7a; color: white; "
        "border-radius: 5px; padding: 3px 8px; font-size: 10px; }"
    )

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(100)
    slider.setValue(0)
    slider.setStyleSheet(
        "QSlider::groove:horizontal { background: #3a4a7a; height: 6px; border-radius: 3px; } "
        "QSlider::handle:horizontal { background: #00ff6a; width: 14px; height: 14px; "
        "margin: -4px 0; border-radius: 7px; } "
        "QSlider::sub-page:horizontal { background: #00ff6a; border-radius: 3px; }"
    )

    time_lbl = QLabel("T: 0.00 s")
    time_lbl.setFont(QFont(ff, 9))
    time_lbl.setStyleSheet("color: #00ff6a; min-width: 80px;")

    prog_lbl = QLabel("0 / 0")
    prog_lbl.setFont(QFont(ff, 8))
    prog_lbl.setStyleSheet("color: #aab2d0; min-width: 70px;")

    for w in (btn_csv, btn_cv, btn_raw, btn_rst, btn_play,
              speed_lbl, speed_combo):
        layout.addWidget(w)

    layout.addWidget(slider, stretch=1)
    layout.addWidget(time_lbl)
    layout.addWidget(prog_lbl)

    return bar


# ──────────────────────────────────────────────
# Status strip
# ──────────────────────────────────────────────
def build_status_strip(ff):
    strip = QHBoxLayout()
    strip.setSpacing(6)

    fields = [
        ("Status",       "No Data"),
        ("Mission Time", "---"),
        ("Altitude",     "--- m"),
        ("GPS",          "---"),
        ("Speed",        "--- m/s"),
    ]

    for name, val in fields:
        lbl = QLabel(f"{name}:  {val}")
        lbl.setFont(QFont(ff, 9, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"color: {C_DARK}; background: {C_PANEL}; "
            f"border-radius: 5px; padding: 3px 10px;"
        )
        strip.addWidget(lbl)

    return strip


# ──────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────
class PATLayout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PAT – Layout Stage")

        # Load font
        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        self.ff = (QFontDatabase.applicationFontFamilies(font_id)[0]
                   if font_id != -1 else "Courier New")

        self._build()

    def _build(self):
        # ── Title banner ──
        banner = QLabel("PAT  –  Postflight Analysis Tracker  |  LASER · UnityRise · PL-26")
        banner.setAlignment(Qt.AlignCenter)
        banner.setFixedHeight(48)
        banner.setFont(QFont(self.ff, 15, QFont.Weight.Bold))
        banner.setStyleSheet(
            f"background-color: {C_DARK}; color: white; "
            f"border-radius: 10px; padding: 5px; letter-spacing: 1px;"
        )

        # ── Three content columns wrapped in white cards ──
        left_card   = card(build_left_column(self.ff))
        middle_card = card(build_middle_column(self.ff))
        right_card  = card(build_right_column(self.ff))

        cols = QHBoxLayout()
        cols.setSpacing(8)
        cols.addWidget(left_card,   stretch=2)
        cols.addWidget(middle_card, stretch=2)
        cols.addWidget(right_card,  stretch=3)

        # ── Root layout ──
        root = QVBoxLayout()
        root.setSpacing(6)
        root.setContentsMargins(10, 8, 10, 8)
        root.addWidget(banner)
        root.addLayout(build_status_strip(self.ff))
        root.addLayout(cols, stretch=1)
        root.addWidget(build_playback_bar(self.ff))

        container = QWidget()
        container.setLayout(root)
        container.setStyleSheet(f"background-color: {C_BG};")
        self.setCentralWidget(container)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PATLayout()
    window.showMaximized()
    sys.exit(app.exec())