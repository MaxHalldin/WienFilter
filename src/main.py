import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from interfaces.pico_output import PicoOutput
from interfaces.calibration import LinearCalibration
from output_component import OutputComponent

# Define intefaces:
MAX_VOLTAGE = 10
port = 'COM3'
cal = LinearCalibration(10)
pico = PicoOutput(port, cal)

# Setup GUI

# (fixes resolution issues on some screens)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)

with pico:
    pico.target = 0 # Initialize voltage at 0
    win = OutputComponent(MAX_VOLTAGE, pico)
    win.show()
    sys.exit(app.exec())