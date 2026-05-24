# Program: PAT.py
# Author:
# Module:
# Email:
# Student Number:
# -----------------------------------------------------------------------------------------------------------------------------
# Code

import sys
import os

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSlider, QFrame, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase

#Paths
BASE_DIRECTORY   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIRECTORY = os.path.join(BASE_DIRECTORY, "Assets")
FONT_NAME = "Assets/Orbitron-VariableFont_wght.ttf"
FONT_PATH = (
    os.path.join(ASSETS_DIRECTORY, FONT_NAME)
    if os.path.exists(os.path.join(ASSETS_DIRECTORY, FONT_NAME))
    else os.path.join(BASE_DIRECTORY, FONT_NAME)
)

#Colour Scheme
BLUE = "#212b58"
PANEL = "#f0f2f7"
WHITE = "#ffffff"
PAGE = "#e8ecf5"
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

def sectionPillLabel(text, ff):
    label = QLabel(text)
    label.setFont(QFont(ff, 8, QFont.Weight.Bold))
    label.setFixedHeight(20)
    label.setStyleSheet(
        f"color: white; background-color: {BLUE}; "
        f"border-radius: 4px; padding: 1px 8px;"
    )
    return label


def placeHolderBox(text, minimumHeight=0):
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(
        f"background-color: {PANEL}; color: #8892b0; "
        f"border: 1px dashed {BORDER}; border-radius: 6px; "
        f"font-size: 11px;"
    )
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    if minimumHeight:
        label.setMinimumHeight(minimumHeight)
    return label

def heightSplitter():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER};")
    line.setFixedHeight(2)
    return line

def cardWidget(layout):
    widget = QWidget()
    widget.setLayout(layout)
    widget.setStyleSheet(
        f"background-color: {WHITE}; border-radius: 10px;"
    )
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
    column.addWidget(placeHolderBox("2D Plot\n(Top)", minimumHeight=80), stretch=1)
    column.addWidget(heightSplitter())

    #Bottom 2D Plot
    column.addWidget(sectionPillLabel("Bottom Plot Variable", ff))
    bottomCombo = QComboBox()
    bottomCombo.addItems(["gpsSpeed", "bmpAltitude", "gpsAltitude", "accelX", "accelY", "accelZ", "gyroX", "gyroY", "gyroZ", "magX", "magY", "magZ", "imuTemp", "bmpTemp", "bmpPressure"])
    bottomCombo.setStyleSheet(COMBO_STYLE)
    column.addWidget(bottomCombo)
    column.addWidget(placeHolderBox("2D Plot\n(Bottom)", minimumHeight=80), stretch=1)
 
    return column


def middle3DColumn(ff):
    column = QVBoxLayout()
    column.setSpacing(6)
    column.setContentsMargins(8, 8, 8, 8)

    column.addWidget(sectionPillLabel("3D Graph", ff))
    GraphCombo = QComboBox()
    GraphCombo.addItems(["Live INS Relative Position (XYZ)"])
    GraphCombo.setStyleSheet(COMBO_STYLE)
    column.addWidget(GraphCombo)
    column.addWidget(placeHolderBox("3D Graph", minimumHeight=80), stretch=1)
    column.addWidget(heightSplitter())

    #Map
    column.addWidget(sectionPillLabel("Map", ff))
    column.addWidget(placeHolderBox("Map View", minimumHeight=80), stretch=1)
 
    return column


def rightHandSideColumn(ff):
    column = QVBoxLayout()
    column.setSpacing(6)
    column.setContentsMargins(8, 8, 8, 8)
 
    #Camera Feed
    column.addWidget(sectionPillLabel("Camera Feed", ff))
 
    cameraRow = QHBoxLayout()
    cameraRow.setSpacing(4)
    cameraRow.addWidget(placeHolderBox("VEGA Computer Vision Feed", minimumHeight=60))
    cameraRow.addWidget(placeHolderBox("Raw Camera Feed",      minimumHeight=60))
    cameraWidget = QWidget()
    cameraWidget.setLayout(cameraRow)
    cameraWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    column.addWidget(cameraWidget, stretch=3)   # camera takes ~75 % of right col
 
    column.addWidget(heightSplitter())

    #Avionics Status Grid
    column.addWidget(sectionPillLabel("Avionics Status", ff))
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
    avionicsGrid = QGridLayout()
    avionicsGrid.setSpacing(3)
    avionicsGrid.setContentsMargins(4,4,4,4)

    for index, (name, value) in enumerate(AVIONICS_FIELDS):
        row, columnOffset = divmod(index, 2)
        nameLabel = QLabel(f"{name}:")
        nameLabel.setFont(QFont(ff, 8, QFont.Weight.Bold))
        nameLabel.setStyleSheet(f"color: {BLUE};")

        valueLabel = QLabel(value)
        valueLabel.setFont(QFont(ff, 8))
        valueLabel.setStyleSheet("color: #555;")
        valueLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
 
        base = columnOffset * 2
        avionicsGrid.addWidget(nameLabel, row, base)
        avionicsGrid.addWidget(valueLabel,  row, base + 1)

    avionicsWidget = QWidget()
    avionicsWidget.setLayout(avionicsGrid)
    avionicsWidget.setStyleSheet(f"background-color: {PANEL}; border-radius: 6px;")
    avionicsWidget.setMaximumHeight(260)
    avionicsWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    column.addWidget(avionicsWidget, stretch=1)
 
    return column


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
 
    buttonCSV = darkButton("CSV")
    buttonVEGA  = darkButton("VEGA Video")
    buttonRaw = darkButton("Raw Video")
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
 
    return bar

#Avioncs status grid
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


#Main Window
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
        self.ff = font_families[0]
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

        leftHandSideWidget = cardWidget(leftHandSide2DColumn(self.ff))
        middleWidget = cardWidget(middle3DColumn(self.ff))
        rightHandSideWidget = cardWidget(rightHandSideColumn(self.ff))
 
        columns = QHBoxLayout()
        columns.setSpacing(8)
        columns.addWidget(leftHandSideWidget, stretch=2)
        columns.addWidget(middleWidget, stretch=2)
        columns.addWidget(rightHandSideWidget, stretch=3)
 
        rootLayout = QVBoxLayout()
        rootLayout.setSpacing(6)
        rootLayout.setContentsMargins(10, 8, 10, 8)
        rootLayout.addWidget(titleBanner)
        rootLayout.addLayout(avionicsStatusGrid(self.ff))
        rootLayout.addLayout(columns, stretch=1)
        rootLayout.addWidget(playBackBar(self.ff))
 
        container = QWidget()
        container.setLayout(rootLayout)
        container.setStyleSheet(f"background-color: {PAGE};")
        self.setCentralWidget(container)
 
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PATMainLayout()
    window.showMaximized()
    sys.exit(app.exec())
