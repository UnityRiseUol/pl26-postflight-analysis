# Program: PAT.py
# Author:
# Module:
# Email:
# Student Number:
# -----------------------------------------------------------------------------------------------------------------------------
# Code

import sys
import os
import numpy as np
import csv
import time
import math
import threading
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QSlider, QFrame, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWebEngineWidgets import QWebEngineView

# ================= CONFIG & ENVIRONMENT =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIRECTORY = BASE_DIR  

ASSETS_DIRECTORY = os.path.join(BASE_DIR, "Assets")
TILE_DIR = os.path.join(BASE_DIR, "tiles")

# Handle font settings safely
FONT_NAME = "Orbitron-VariableFont_wght.ttf"
FONT_PATH = (
    os.path.join(ASSETS_DIRECTORY, FONT_NAME)
    if os.path.exists(os.path.join(ASSETS_DIRECTORY, FONT_NAME))
    else os.path.join(BASE_DIR, FONT_NAME)
)

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"

# University of Liverpool EEE Building Coordinates
LAUNCH_LAT = 53.4065
LAUNCH_LON = -2.9665
SIM_DT = 0.03

# ================= UI COLOR SCHEME =================
BLUE   = "#212b58"
PANEL  = "#f0f2f7"
WHITE  = "#ffffff"
PAGE   = "#e8ecf5"
BORDER = "#d0d5e8"

COMBO_STYLE = (
    "QComboBox { color: white; background-color: #212b58; "
    "border-radius: 5px; padding: 3px 8px; font-size: 10px; } "
    "QComboBox QAbstractItemView { background: #212b58; color: white; }"
)

BUTTON_DARK = (
    "QPushButton { background-color: #3a4a7a; color: white; "
    "border-radius: 5px; padding: 4px 12px; font-size: 11px; } "
    "QPushButton:hover { background-color: #4a5a9a; }"
)

BUTTON_PLAY = (
    "QPushButton { background-color: white; color: #212b58; "
    "border-radius: 5px; padding: 4px 18px; font-size: 11px; font-weight: bold; } "
    "QPushButton:hover { background-color: #f0f2f7; }"
)

# ================= TILE SERVER =================
def start_tile_server():
    os.chdir(BASE_DIR)
    server = HTTPServer(("127.0.0.1", 8000), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("🌐 Server running at http://127.0.0.1:8000")

# ================= TILE DOWNLOAD SYSTEM =================
def deg2tile(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(
        math.tan(math.radians(lat)) +
        1 / math.cos(math.radians(lat))
    ) / math.pi) / 2.0 * n)
    return x, y

def download_tile(z, x, y):
    path = os.path.join(TILE_DIR, str(z), str(x), f"{y}.png")
    if os.path.exists(path):
        return

    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "QtRocketSim/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read()

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    except Exception:
        pass

def ensure_tiles():
    print("📦 Downloading missing map tiles...")
    for z in range(12, 16):
        cx, cy = deg2tile(LAUNCH_LAT, LAUNCH_LON, z)
        radius = 5
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                download_tile(z, cx + dx, cy + dy)
    print("✅ Tiles synchronized offline")

# ================= LEAFLET HTML STRATEGY (OPTION A) =================
HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="http://127.0.0.1:8000/leaflet.css"/>
<script src="http://127.0.0.1:8000/leaflet.js"></script>
<style>
html, body, #map {{ height: 100%; margin: 0; background-color: #f0f2f7; }}
.rocket {{
  width: 14px;
  height: 14px;
  background: #00aaff;
  border-radius: 50%;
  box-shadow: 0 0 12px #00aaff;
}}
.launch {{
  width: 10px;
  height: 10px;
  background: red;
  border-radius: 50%;
  box-shadow: 0 0 10px red;
}}
</style>
</head>
<body>
<div id="map"></div>
<script>
const LAUNCH_LAT = {LAUNCH_LAT};
const LAUNCH_LON = {LAUNCH_LON};

var map = L.map('map', {{
    zoomControl: false,
    attributionControl: false,
    minZoom: 12,
    maxZoom: 15
}}).setView([LAUNCH_LAT, LAUNCH_LON], 14);

L.tileLayer('http://127.0.0.1:8000/tiles/{{z}}/{{x}}/{{y}}.png', {{
    minZoom: 12,
    maxZoom: 15
}}).addTo(map);

var launch = L.marker([LAUNCH_LAT, LAUNCH_LON], {{
    icon: L.divIcon({{ className: "launch" }})
}}).addTo(map);

var rocket = L.marker([LAUNCH_LAT, LAUNCH_LON], {{
    icon: L.divIcon({{ className: "rocket" }})
}}).addTo(map);

var path = L.polyline([], {{color: '#212b58', weight: 3.5}}).addTo(map);

window.updateMarker = function(lat, lon) {{
    rocket.setLatLng([lat, lon]);
    path.addLatLng([lat, lon]);
    
    var dist = Math.sqrt(Math.pow(lat - LAUNCH_LAT, 2) + Math.pow(lon - LAUNCH_LON, 2));
    
    if (dist > 0.0001) {{
        map.fitBounds(L.latLngBounds([[LAUNCH_LAT, LAUNCH_LON], [lat, lon]]).pad(0.3));
    }} else {{
        map.setView([LAUNCH_LAT, LAUNCH_LON], 14);
    }}
}};

window.resetMapFramework = function() {{
    path.setLatLngs([]);
    rocket.setLatLng([LAUNCH_LAT, LAUNCH_LON]);
    map.setView([LAUNCH_LAT, LAUNCH_LON], 14);
}};
</script>
</body>
</html>
"""

# ================= MATPLOTLIB WIDGETS =================
class Plot2D(FigureCanvas):
    def __init__(self, title, ylabel):
        self.figure = Figure(tight_layout=True)
        self.axis   = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.times  = []
        self.values = []
        self._styleAxes(title, ylabel)

    def _styleAxes(self, title, ylabel):
        self.axis.set_title(title, fontsize=9, color=BLUE, fontweight="bold")
        self.axis.set_xlabel("Time (s)", fontsize=8)
        self.axis.set_ylabel(ylabel, fontsize=8)
        self.axis.grid(True, alpha=0.3)
        self.axis.tick_params(labelsize=7)
        self.figure.patch.set_facecolor(PANEL)
        self.axis.set_facecolor(PANEL)
        self.line, = self.axis.plot([], [], lw=1.5, color=BLUE)

    def resetPlot(self, title, ylabel):
        self.axis.clear()
        self.times.clear()
        self.values.clear()
        self._styleAxes(title, ylabel)
        self.draw()

    def updatePlot(self):
        if not self.times:
            return
        self.line.set_data(self.times, self.values)
        self.axis.relim()
        self.axis.autoscale_view()
        self.draw_idle()

class Plot3D(FigureCanvas):
    def __init__(self):
        self.figure = Figure(tight_layout=True)
        self.axis   = self.figure.add_subplot(111, projection="3d")
        super().__init__(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.positionX, self.positionY, self.positionZ = [], [], []
        self.figure.patch.set_facecolor(PANEL)
        self._styleAxes()

    def _styleAxes(self):
        self.axis.set_title("Live INS Relative Position (XYZ)", fontsize=9, fontweight="bold", color=BLUE)
        self.axis.set_xlabel("X (m)", fontsize=7)
        self.axis.set_ylabel("Y (m)", fontsize=7)
        self.axis.set_zlabel("Z (m)", fontsize=7)
        self.axis.tick_params(labelsize=6)
        self.axis.set_facecolor(PANEL)

    def updatePlot(self):
        if not self.positionX:
            return
        self.axis.clear()
        self._styleAxes()
        self.axis.plot(self.positionX, self.positionY, self.positionZ, lw=1.5, color=BLUE)
        self.axis.scatter([self.positionX[-1]], [self.positionY[-1]], [self.positionZ[-1]], s=50, color="red", zorder=5)
        self.draw_idle()

# ================= HELPER FUNCTIONS =================
def sectionPillLabel(text, ff):
    label = QLabel(text)
    label.setFont(QFont(ff, 8, QFont.Weight.Bold))
    label.setFixedHeight(20)
    label.setStyleSheet(f"color: white; background-color: {BLUE}; border-radius: 4px; padding: 1px 8px;")
    return label

def heightSplitter():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER};")
    line.setFixedHeight(2)
    return line

# ================= MAIN APPLICATION FRAME =================
class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Liverpool Rocket Tracker - Consolidated UI")
        self.resize(1280, 800)

        # Main Layout Scaffold
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        base_layout = QHBoxLayout(main_widget)
        base_layout.setContentsMargins(10, 10, 10, 10)
        base_layout.setSpacing(10)

        # Left Panel (Telemetry Graphics Dashboard)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot2d_1 = Plot2D("Altitude Profile", "Altitude (m)")
        self.plot2d_2 = Plot2D("Velocity Track", "Velocity (m/s)")
        self.plot3d = Plot3D()

        left_layout.addWidget(self.plot2d_1)
        left_layout.addWidget(self.plot2d_2)
        left_layout.addWidget(self.plot3d)
        base_layout.addWidget(left_panel, stretch=1)

        # Right Panel (Geospatial Web Map Frame)
        self.view = QWebEngineView()
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        base_layout.addWidget(self.view, stretch=2)

        # Mount HTML directly onto local asset server context 
        self.view.setHtml(HTML, QUrl("http://127.0.0.1:8000/"))
        self.view.loadFinished.connect(self.handle_load_finished)

        # Data Mechanics Variables
        self.data = self.load_csv("test_flight_data.csv")
        self.t = 0.0
        self.i = 0
        self.s_lat = None
        self.s_lon = None
        self.alpha = 0.1

        self.timer = QTimer()
        self.timer.setInterval(int(SIM_DT * 1000))
        self.timer.timeout.connect(self.step)

    def handle_load_finished(self, success):
        if success:
            QTimer.singleShot(750, self.start)
        else:
            print("⚠️ Web view failed to reach asset server context.")

    def start(self):
        self.timer.start()

    def load_csv(self, path):
        data = []
        if not os.path.exists(path):
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["t", "lat", "lon"])
                for step in range(300):
                    writer.writerow([step*0.1, LAUNCH_LAT+(step*0.00003), LAUNCH_LON+(step*0.00005)])
        
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                data.append((float(r["t"]), float(r["lat"]), float(r["lon"])))
        return data

    def interpolate(self, t):
        while self.i < len(self.data) - 2 and self.data[self.i + 1][0] < t:
            self.i += 1

        t1, lat1, lon1 = self.data[self.i]
        t2, lat2, lon2 = self.data[self.i + 1]
        r = (t - t1) / (t2 - t1 + 1e-9)
        return (lat1 + (lat2 - lat1) * r, lon1 + (lon2 - lon1) * r)

    def step(self):
        self.t += SIM_DT
        if self.i >= len(self.data) - 2:
            self.timer.stop()
            return

        lat, lon = self.interpolate(self.t)

        if self.s_lat is None:
            self.s_lat, self.s_lon = lat, lon
        else:
            self.s_lat = self.alpha * lat + (1 - self.alpha) * self.s_lat
            self.s_lon = self.alpha * lon + (1 - self.alpha) * self.s_lon

        # Push coordinate vectors out into the Javascript rendering framework
        js = f"window.updateMarker({self.s_lat}, {self.s_lon});"
        self.view.page().runJavaScript(js)

        # Mock values generated to sync standard graph displays dynamically alongside maps
        self.plot2d_1.times.append(self.t)
        self.plot2d_1.values.append(math.sin(self.t * 0.2) * 150 + (self.t * 10))
        self.plot2d_1.updatePlot()

        self.plot2d_2.times.append(self.t)
        self.plot2d_2.values.append(abs(math.cos(self.t * 0.2) * 45))
        self.plot2d_2.updatePlot()

        self.plot3d.positionX.append((lon - LAUNCH_LON) * 10000)
        self.plot3d.positionY.append((lat - LAUNCH_LAT) * 10000)
        self.plot3d.positionZ.append(math.sin(self.t * 0.2) * 150 + (self.t * 10))
        self.plot3d.updatePlot()


def cardWidget(layout):
    widget = QWidget()
    widget.setLayout(layout)
    widget.setStyleSheet(f"background-color: {WHITE}; border-radius: 10px;")
    return widget


def leftHandSide2DColumn(ff):
    column = QVBoxLayout()
    column.setSpacing(6)
    column.setContentsMargins(8,8,8,8)

    #Top 2D Plot
    column.addWidget(sectionPillLabel("Top Plot Variable", ff))
    topCombo = QComboBox()
    topCombo.addItems(["bmpAltitude", "gpsAltitude", "gpsSpeed", "accelX", "accelY", "accelZ", "gyroX", "gyroY", "gyroZ", "magX", "magY", "magZ", "imuTemp", "bmpTemp", "bmpPressure"])
    topCombo.setStyleSheet(COMBO_STYLE)
    column.addWidget(topCombo)
    topPlot = Plot2D("bmpAltitude vs Time", "bmpAltitude (m)")
    column.addWidget(topPlot, stretch=1)
    column.addWidget(heightSplitter())

    #Bottom 2D Plot
    column.addWidget(sectionPillLabel("Bottom Plot Variable", ff))
    bottomCombo = QComboBox()
    bottomCombo.addItems(["gpsSpeed", "bmpAltitude", "gpsAltitude", "accelX", "accelY", "accelZ", "gyroX", "gyroY", "gyroZ", "magX", "magY", "magZ", "imuTemp", "bmpTemp", "bmpPressure"])
    bottomCombo.setStyleSheet(COMBO_STYLE)
    column.addWidget(bottomCombo)
    bottomPlot = Plot2D("gpsSpeed vs Time", "gpsSpeed (m/s)")
    column.addWidget(bottomPlot, stretch=1)

    return column, topCombo, topPlot, bottomCombo, bottomPlot


def middle3DColumn(ff):
    column = QVBoxLayout()
    column.setSpacing(6)
    column.setContentsMargins(8, 8, 8, 8)

    column.addWidget(sectionPillLabel("3D Graph", ff))
    GraphCombo = QComboBox()
    GraphCombo.addItems(["Live INS Relative Position (XYZ)"])
    GraphCombo.setStyleSheet(COMBO_STYLE)
    column.addWidget(GraphCombo)
    plot3d = Plot3D()
    column.addWidget(plot3d, stretch=1)
    column.addWidget(heightSplitter())

    # Functional Map Component
    column.addWidget(sectionPillLabel("Map", ff))
    mapView = QWebEngineView()
    column.addWidget(mapView, stretch=1)
    return column, plot3d, mapView


def rightHandSideColumn(ff):
    column = QVBoxLayout()
    column.setSpacing(6)
    column.setContentsMargins(8, 8, 8, 8)

    #Camera Feed
    column.addWidget(sectionPillLabel("Onboard Camera Feed", ff))
    vegaLabel = QLabel("VEGA Rideshare\n\n(Load a video to begin)")
    vegaLabel.setAlignment(Qt.AlignCenter)
    vegaLabel.setStyleSheet(
        "background-color: #1a1a2e; color: #aab2d0; "
        f"border: 1px solid {BLUE}; border-radius: 6px; font-size: 11px;"
    )
    vegaLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    vegaLabel.setMinimumHeight(80)

    rawVideoLabel = QLabel("🎥  Raw Camera Feed\n\n(Load a video to begin)")
    rawVideoLabel.setAlignment(Qt.AlignCenter)
    rawVideoLabel.setStyleSheet(
        "background-color: #1a1a2e; color: #aab2d0; "
        f"border: 1px solid {BLUE}; border-radius: 6px; font-size: 11px;"
    )
    rawVideoLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    rawVideoLabel.setMinimumHeight(80)

    column.addWidget(vegaLabel, stretch=1)
    column.addWidget(rawVideoLabel, stretch=1)
    column.addWidget(heightSplitter())

    #Avionics Status Grid
    column.addWidget(sectionPillLabel("Avionics Status", ff))
    AVIONICS_FIELDS = [
        ("GPS Fix",      "gpsFixMillis",  "ms"),   ("GPS Valid",    "gpsValid",     ""),
        ("GPS Speed",    "gpsSpeed",      "m/s"),  ("GPS Heading",  "gpsHeading",   "°"),
        ("Accel X",      "accelX",        "g"),    ("Accel Y",      "accelY",       "g"),
        ("Accel Z",      "accelZ",        "g"),    ("Gyro X",       "gyroX",        "°/s"),
        ("Gyro Y",       "gyroY",         "°/s"),  ("Gyro Z",       "gyroZ",        "°/s"),
        ("Mag X",        "magX",          "raw"),  ("Mag Y",        "magY",         "raw"),
        ("Mag Z",        "magZ",          "raw"),  ("IMU Temp",     "imuTemp",      "°C"),
        ("BMP Temp",     "bmpTemp",       "°C"),   ("BMP Pressure", "bmpPressure",  "hPa"),
    ]
    avionicsGrid = QGridLayout()
    avionicsGrid.setSpacing(3)
    avionicsValueLabels = {}
    avionicsGrid.setContentsMargins(4, 4, 4, 4)
    for index, (name, csvKey, unit) in enumerate(AVIONICS_FIELDS):
        row, columnOffset = divmod(index, 2)
        nameLabel = QLabel(f"{name}:")
        nameLabel.setFont(QFont(ff, 8, QFont.Weight.Bold))
        nameLabel.setStyleSheet(f"color: {BLUE};")
        valueLabel = QLabel("---")
        valueLabel.setFont(QFont(ff, 8))
        valueLabel.setStyleSheet("color: #555;")
        valueLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        base = columnOffset * 2
        avionicsGrid.addWidget(nameLabel,  row, base)
        avionicsGrid.addWidget(valueLabel, row, base + 1)
        avionicsValueLabels[csvKey] = (valueLabel, unit)
    avionicsWidget = QWidget()
    avionicsWidget.setLayout(avionicsGrid)
    avionicsWidget.setStyleSheet(f"background-color: {PANEL}; border-radius: 6px;")
    avionicsWidget.setMaximumHeight(260)
    avionicsWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    column.addWidget(avionicsWidget, stretch=1)

    return column, avionicsValueLabels, vegaLabel, rawVideoLabel


def playBackBar(ff):
    bar = QWidget()
    bar.setFixedHeight(48)
    bar.setStyleSheet(f"background-color: {BLUE}; border-radius: 8px;")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(12, 6, 12, 6)
    layout.setSpacing(8)

    def darkButton(text):
        button = QPushButton(text)
        button.setStyleSheet(BUTTON_DARK)
        button.setFont(QFont(ff, 9))
        return button

    buttonCSV   = darkButton("CSV")
    buttonVEGA  = darkButton("VEGA Video")
    buttonRaw   = darkButton("Raw Video")
    buttonReset = darkButton("Restart")

    buttonPlay = QPushButton("Play")
    buttonPlay.setStyleSheet(BUTTON_PLAY)
    buttonPlay.setFont(QFont(ff, 9, QFont.Weight.Bold))

    playBackSpeedLabel = QLabel("Speed:")
    playBackSpeedLabel.setStyleSheet("color: white; font-size: 10px;")
    playBackSpeedLabel.setFont(QFont(ff, 9))

    playBackSpeedCombo = QComboBox()
    playBackSpeedCombo.addItems(["0.25×", "0.5×", "1×", "2×", "5×", "10×"])
    playBackSpeedCombo.setCurrentIndex(2)
    playBackSpeedCombo.setStyleSheet(
        "QComboBox { background-color: #3a4a7a; color: white; "
        "border-radius: 5px; padding: 3px 8px; font-size: 10px; }"
    )

    playBackSlider = QSlider(Qt.Horizontal)
    playBackSlider.setMinimum(0)
    playBackSlider.setMaximum(100)
    playBackSlider.setValue(0)
    playBackSlider.setStyleSheet(
        "QSlider::groove:horizontal { background: #3a4a7a; height: 6px; border-radius: 3px; } "
        "QSlider::handle:horizontal { background: white; width: 14px; height: 14px; "
        "margin: -4px 0; border-radius: 7px; } "
        "QSlider::sub-page:horizontal { background: white; border-radius: 3px; }"
    )

    timeLabel = QLabel("T: 0.00 s")
    timeLabel.setFont(QFont(ff, 9))
    timeLabel.setStyleSheet("color: white; min-width: 80px;")

    progressLabel = QLabel("0 / 0")
    progressLabel.setFont(QFont(ff, 8))
    progressLabel.setStyleSheet("color: #aab2d0; min-width: 70px;")

    for w in (buttonCSV, buttonVEGA, buttonRaw, buttonReset, buttonPlay, playBackSpeedLabel, playBackSpeedCombo):
        layout.addWidget(w)
    layout.addWidget(playBackSlider, stretch=1)
    layout.addWidget(timeLabel)
    layout.addWidget(progressLabel)

    return bar, buttonCSV, buttonVEGA, buttonRaw, buttonReset, buttonPlay, playBackSpeedCombo, playBackSlider, timeLabel, progressLabel


def avionicsStatusGrid(ff):
    statusGrid = QHBoxLayout()
    statusGrid.setSpacing(6)
    status = [
        ("Status",       "No Data"),
        ("Mission Time", "---"),
        ("Altitude",     "--- m"),
        ("GPS",          "---"),
        ("Speed",        "--- m/s"),
    ]
    for name, value in status:
        label = QLabel(f"{name}:  {value}")
        label.setFont(QFont(ff, 9, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"color: {BLUE}; background: {PANEL}; "
            f"border-radius: 5px; padding: 3px 10px;"
        )
        statusGrid.addWidget(label)
    return statusGrid


class PATMainLayout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PAT - Postflight Analysis Tracker")
        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        font_families = (
            QFontDatabase.applicationFontFamilies(font_id)
            if font_id != -1
            else []
        )
        self.ff = font_families[0] if font_families else "Courier New"
        self._build()

    def _build(self):
        titleBanner = QLabel("PAT - Postflight Analysis Tracker  |  LASER - UnityRise - PL-26")
        titleBanner.setAlignment(Qt.AlignCenter)
        titleBanner.setFixedHeight(48)
        titleBanner.setFont(QFont(self.ff, 15, QFont.Weight.Bold))
        titleBanner.setStyleSheet(
            f"background-color: {BLUE}; color: white; "
            f"border-radius: 10px; padding: 5px; letter-spacing: 1px;"
        )

        leftLayout, self.topCombo, self.topPlot, self.bottomCombo, self.bottomPlot = leftHandSide2DColumn(self.ff)
        middleLayout, self.plot3d, self.mapView = middle3DColumn(self.ff)
        rightLayout, self.avionicsValueLabels, self.vegaLabel, self.rawVideoLabel = rightHandSideColumn(self.ff)
        
        # Deploy Leaflet Blueprint inside WebEngine View
        self.mapView.setHtml(HTML, QUrl("http://127.0.0.1:8000/"))

        self.topCombo.currentTextChanged.connect(self.onTopVariableChanged)
        self.bottomCombo.currentTextChanged.connect(self.onBottomVariableChanged)

        (playBar, self.buttonCSV, self.buttonVEGA, self.buttonRaw, self.buttonReset, self.buttonPlay, self.playBackSpeedCombo, self.playBackSlider, self.timeLabel, self.progressLabel) = playBackBar(self.ff)

        self.buttonCSV.clicked.connect(self.onLoadCSV)
        self.buttonPlay.clicked.connect(self.onPlay)
        self.buttonReset.clicked.connect(self.onRestart)
        self.playBackSpeedCombo.currentIndexChanged.connect(self.onPlayBackSpeedChanged)
        self.playBackSlider.sliderMoved.connect(self.onSliderMoved)
        self.buttonVEGA.clicked.connect(self.onLoadVegaVideo)
        self.buttonRaw.clicked.connect(self.onLoadRawVideo)

        #Playback state
        self.allRows   = []
        self.playIndex = 0
        self.playing   = False
        self.speed     = 1.0
        self.startTime = None
        self.startIndex = 0
        self.playbackSpeeds = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]

        self.capVega  = None
        self.capRawVideo = None
        self.videoTimer = QTimer()
        self.videoTimer.timeout.connect(self.onVideoTick)
        self.videoTimer.start(33)

        self.statusStrip = avionicsStatusGrid(self.ff)
        statusWidgets = []
        for index in range(self.statusStrip.count()):
            item = self.statusStrip.itemAt(index)
            if item and item.widget():
                statusWidgets.append(item.widget())
        self.labelStatus, self.labelMissionTime, self.labelAltitude, self.labelGPS, self.labelSpeed = statusWidgets

        self.replayTimer = QTimer()
        self.replayTimer.timeout.connect(self.playback)
        self.replayTimer.start(30)

        columns = QHBoxLayout()
        columns.setSpacing(8)
        columns.addWidget(cardWidget(leftLayout),   stretch=2)
        columns.addWidget(cardWidget(middleLayout),   stretch=2)
        columns.addWidget(cardWidget(rightLayout), stretch=3)

        rootLayout = QVBoxLayout()
        rootLayout.setSpacing(6)
        rootLayout.setContentsMargins(10, 8, 10, 8)
        rootLayout.addWidget(titleBanner)
        rootLayout.addLayout(self.statusStrip)
        rootLayout.addLayout(columns, stretch=1)
        rootLayout.addWidget(playBar)

        container = QWidget()
        container.setLayout(rootLayout)
        container.setStyleSheet(f"background-color: {PAGE};")
        self.setCentralWidget(container)

    def onTopVariableChanged(self, variable):
        self.topPlot.resetPlot(f"{variable} vs Time", variable)

    def onBottomVariableChanged(self, variable):
        self.bottomPlot.resetPlot(f"{variable} vs Time", variable)

    def onLoadCSV(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Flight CSV", BASE_DIRECTORY, "CSV Files (*.csv)")
        if not path:
            return
        rows = []
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    rows.append({k: float(v) for k, v in row.items()})
                except ValueError:
                    continue
        self.allRows = rows
        self.onRestart()
        self.playBackSlider.setMaximum(max(1, len(rows) - 1))
        self.progressLabel.setText(f"0 / {len(rows)}")
        self.labelStatus.setText(f"Status: Ready - {len(rows)} rows")

    def onPlay(self):
        if not self.allRows:
            return
        self.playing = not self.playing
        if self.playing:
            self.startTime = time.time()
            self.startIndex = self.playIndex
            self.buttonPlay.setText("Pause")
        else:
            self.buttonPlay.setText("Play")

    def onRestart(self):
        self.playing = False
        self.playIndex = 0
        self.startIndex = 0
        self.startTime = None
        self.buttonPlay.setText("Play")
        self.playBackSlider.setValue(0)
        self.timeLabel.setText("T: 0.00 s")
        self.topPlot.times.clear()
        self.topPlot.values.clear()
        self.topPlot.resetPlot(f"{self.topCombo.currentText()} vs Time", self.topCombo.currentText())
        self.bottomPlot.times.clear()
        self.bottomPlot.values.clear()
        self.bottomPlot.resetPlot(f"{self.bottomCombo.currentText()} vs Time", self.bottomCombo.currentText())
        self.plot3d.positionX.clear()
        self.plot3d.positionY.clear()
        self.plot3d.positionZ.clear()
        
        if hasattr(self, 'mapView') and self.mapView.page():
            self.mapView.page().runJavaScript("resetMap();")

        if self.capVega and self.capVega.isOpened():
            self.capVega.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.capRawVideo and self.capRawVideo.isOpened():
            self.capRawVideo.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def onPlayBackSpeedChanged(self, index):
        if self.playing:
            self.startTime  = time.time()
            self.startIndex = self.playIndex
        self.speed = self.playbackSpeeds[index]

    def onSliderMoved(self, index):
        self.playIndex  = index
        self.startIndex = index
        if self.playing:
            self.startTime = time.time()
        self._rebuildHistory(index)

    def _rebuildHistory(self, upToIndex):
        self.topPlot.times.clear()
        self.topPlot.values.clear()
        self.bottomPlot.times.clear()
        self.bottomPlot.values.clear()
        self.plot3d.positionX.clear()
        self.plot3d.positionY.clear()
        self.plot3d.positionZ.clear()

        topDisplay = self.topCombo.currentText()
        bottomDisplay = self.bottomCombo.currentText()
        timeZero = self.allRows[0]["millis"] / 1000.0 if self.allRows else 0
        
        coords = []
        for row in self.allRows[:upToIndex + 1]:
            t = row["millis"] / 1000.0 - timeZero
            self.topPlot.times.append(t)
            self.topPlot.values.append(row.get(topDisplay, 0))
            self.bottomPlot.times.append(t)
            self.bottomPlot.values.append(row.get(bottomDisplay, 0))
            self.plot3d.positionX.append(row.get("accelX", 0))
            self.plot3d.positionY.append(row.get("accelY", 0))
            self.plot3d.positionZ.append(row.get("bmpAltitude", 0))
            coords.append([row.get("gpsLatitude", 0), row.get("gpsLongitude", 0)])

        self.topPlot.updatePlot()
        self.bottomPlot.updatePlot()
        self.plot3d.updatePlot()
        self.mapView.page().runJavaScript(f"setPath({coords});")
        
    def playback(self):
        if not self.playing or not self.allRows:
            return

        elapsedTime = (time.time() - self.startTime) * self.speed
        frequency = 0.010
        targetIndex = min(self.startIndex + int(elapsedTime / frequency), len(self.allRows) - 1)
        if targetIndex <= self.playIndex and self.playIndex > 0:
            return

        topDisplay    = self.topCombo.currentText()
        bottomDisplay = self.bottomCombo.currentText()
        timeZero = self.allRows[0]["millis"] / 1000.0

        new_coords = []
        for i in range(self.playIndex, targetIndex + 1):
            row = self.allRows[i]
            t = row["millis"] / 1000.0 - timeZero
            self.topPlot.times.append(t)
            self.topPlot.values.append(row.get(topDisplay, 0))
            self.bottomPlot.times.append(t)
            self.bottomPlot.values.append(row.get(bottomDisplay, 0))
            self.plot3d.positionX.append(row.get("accelX", 0))
            self.plot3d.positionY.append(row.get("accelY", 0))
            self.plot3d.positionZ.append(row.get("bmpAltitude", 0))
            new_coords.append([row.get("gpsLatitude", 0), row.get("gpsLongitude", 0)])

        self.playIndex = targetIndex
        row = self.allRows[self.playIndex]
        t = row["millis"] / 1000.0 - timeZero

        #Update Text Strips
        self.labelMissionTime.setText(f"Mission Time:  {t:.2f} s")
        self.labelAltitude.setText(f"Altitude: {row.get('bmpAltitude', 0):.1f} m")
        self.labelGPS.setText(f"GPS: {row.get('gpsLatitude', 0):.5f}, {row.get('gpsLongitude', 0):.5f}")
        self.labelSpeed.setText(f"Speed: {row.get('gpsSpeed', 0):.2f} m/s")

        for csvKey, (label, unit) in self.avionicsValueLabels.items():
            value = row.get(csvKey, None)
            if value is not None:
                if unit:
                    label.setText(f"{value:.4f} {unit}")
                else:
                    label.setText(f"{value:.4f}")
            else:
                label.setText("---")
        
        self.topPlot.updatePlot()
        self.bottomPlot.updatePlot()
        if self.playIndex % 5 == 0:
            self.plot3d.updatePlot()

        # Update Map Tracking
        if new_coords:
            self.mapView.page().runJavaScript(f"appendPositions({new_coords});")

        self.playBackSlider.setValue(self.playIndex)
        self.timeLabel.setText(f"T: {t:.2f} s")
        self.progressLabel.setText(f"{self.playIndex} / {len(self.allRows)}")

        #Autostop once it gets to the end
        if self.playIndex >= len(self.allRows) - 1:
            self.playing = False
            self.buttonPlay.setText("Play")
            self.labelStatus.setText("Status: Complete")
    
    def onLoadVegaVideo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open CV Video", BASE_DIRECTORY,
            "Video Files (*.mp4 *.avi *.h264 *.mkv *.mov)"
        )
        if not path:
            return
        if self.capVega:
            self.capVega.release()
        self.capVega = cv2.VideoCapture(path)
        if not self.capVega.isOpened():
            self.vegaLabel.setText("VEGA Rideshare Feed\n\n(Could not open file)")
    
    def onLoadRawVideo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Raw Video", BASE_DIRECTORY,
            "Video Files (*.mp4 *.avi *.h264 *.mkv *.mov)"
        )
        if not path:
            return
        if self.capRawVideo:
            self.capRawVideo.release()
        self.capRawVideo = cv2.VideoCapture(path)
        if not self.capRawVideo.isOpened():
            self.rawVideoLabel.setText("Raw Camera Feed\n\n(Could not open file)")  

    def onVideoTick(self):
        if not self.playing or not self.allRows:
            return
        row     = self.allRows[self.playIndex]
        t       = row["millis"] / 1000.0 - self.allRows[0]["millis"] / 1000.0
        tTotal  = (self.allRows[-1]["millis"] - self.allRows[0]["millis"]) / 1000.0
        if tTotal <= 0:
            return
        fraction = t / tTotal

        self._updateFrame(self.capVega,     self.vegaLabel,     fraction)
        self._updateFrame(self.capRawVideo, self.rawVideoLabel, fraction)

    def _updateFrame(self, cap, label, fraction):
        if cap is None or not cap.isOpened():
            return

        totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        if totalFrames > 0:
            targetFrame = int(fraction * totalFrames)
            cap.set(cv2.CAP_PROP_POS_FRAMES, targetFrame)
        elif fps > 0:
            tTotal = self.allRows[-1]["millis"] / 1000.0 - self.allRows[0]["millis"] / 1000.0
            targetMs = fraction * tTotal * 1000.0
            cap.set(cv2.CAP_PROP_POS_MSEC, targetMs)

        returnValue, frame = cap.read()
        if not returnValue:
            return
        labelWidth  = label.width()
        labelHeight = label.height()
        if labelWidth < 10 or labelHeight < 10:
            return
        height, width = frame.shape[:2]
        scale     = min(labelWidth / width, labelHeight / height)
        newWidth  = int(width  * scale)
        newHeight = int(height * scale)
        frame = cv2.resize(frame, (newWidth, newHeight), interpolation=cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, newWidth, newHeight, newWidth * 3, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
    os.makedirs(TILE_DIR, exist_ok=True)
    start_tile_server()
    ensure_tiles()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PATMainLayout()
    window.showMaximized()
    sys.exit(app.exec())
