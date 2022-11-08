import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from output_component import Window

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)

win = Window()
win.show()
sys.exit(app.exec())