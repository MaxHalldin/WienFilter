from __future__ import annotations
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

from pythion._layout.main_window import Ui_MainWindow

class MainWindowComponent(QMainWindow, Ui_MainWindow):
    _instance: MainWindowComponent = None
    _app: QApplication = None

    def __new__(cls, *args, **kwargs):
        # This __new__ method serves two purposes: enforcing a singleton pattern (i.e. only one MainWindowComponent may ever
        # be instantiated), and instantiating the QApplication object. 

        if cls._instance is None: # Only run once! 

            # Do some initial configuration of Qt
            # The following four lines fix some resolution issues.
            if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

            # The Qapplication must be instantiated before any QWidgets, hence the class variable
            cls._app = QApplication(sys.argv)
            # Finally, instantiate and return this object through a call to super().__new__()
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Boilerplate initialization
        super().__init__(None)
        self.setupUi(self)

    def add_children(self, *children) -> None:
        for child in children:
            self.mainLayout.addWidget(child)

    def run(self):
        self.show()
        sys.exit(self._app.exec())