import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

# Hardware interface classes
from interfaces.output import MockOutput, PicoOutput
from interfaces.calibration import LinearCalibration

# GUI Classes
from output_component import OutputComponent
from main_window_component import MainWindowComponent

# Define hardware intefaces:
MAX_VOLTAGE = 10
port = 'COM3'
cal = LinearCalibration(10)
pico = PicoOutput(port, cal, MAX_VOLTAGE)

mock = MockOutput()
# Setup GUI

# (fixes resolution issues on some screens)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)

with pico, mock:
    pico.target = 0 # Initialize voltage at 0
    win = MainWindowComponent()
    output_component1 = OutputComponent(MAX_VOLTAGE, pico, parent=win)
    output_component2 = OutputComponent(350, mock, parent=win)
    win.add_children(output_component1, output_component2)
    win.show()
    sys.exit(app.exec())