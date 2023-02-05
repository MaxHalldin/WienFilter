from __future__ import annotations

from typing import ClassVar, Any
import sys
import traceback
import matplotlib.pyplot as plt

import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from pythion._gui.layout.ui_main_window import Ui_MainWindow


logger = logging.getLogger('pythion')


class MainWindow(QMainWindow, Ui_MainWindow):
    _instance: ClassVar[MainWindow | None] = None
    _app: ClassVar[QApplication]

    def __new__(cls, *args: Any, **kwargs: Any) -> MainWindow:
        # This __new__ method serves two purposes: enforcing a singleton pattern (i.e. only one MainWindowComponent may ever
        # be instantiated), and instantiating the QApplication object.
        if cls._instance is None:  # Only run once!
            # Do some initial configuration of Qt
            if 'high_resolution' in kwargs and kwargs['high_resolution']:
                # The following four lines enables using the system dpi settings - however - they aren't compatible with matplotlib
                if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
                    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
                if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
                    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

            # The Qapplication must be instantiated before any QWidgets, hence the class variable
            cls._app = QApplication(sys.argv)
            # Finally, instantiate and return this object through a call to super().__new__()
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, high_resolution: bool = False, master_error_handler=None) -> None:
        if master_error_handler is None:
            # If no error handler is provided, declare a function that does nothing
            self.master_error_handler = lambda *_: None
        else:
            self.master_error_handler = master_error_handler
        # Boilerplate initialization
        super().__init__(None)
        # Custom initialization
        self.setupUi(self)  # type: ignore

    def main_widget(self) -> QWidget:
        return self.horizontalLayoutWidget

    def add_children(self, *children: QWidget) -> None:
        for child in children:
            self.mainLayout.addWidget(child)

    def run(self) -> None:
        sys.excepthook = self.excepthook
        self.setWindowTitle("Selection of Ion Mass - Beam Analysis (SIMBA)")
        self.show()
        logger.info('                Program starts')
        exit_code = self._app.exec()
        if exit_code == 0:
            logger.info('                Program exited normally')
        else:
            logger.info('                Successfully exited program after exception')
        return exit_code

    def closeEvent(self, _: Any):
        """
        Close all open plots (must be called before Qt Application exits).
        closeEvent will automatically be called when widget is destoyed, and is not explicitly called here.
        """
        plt.close('all')

    def excepthook(self, exc_type, exc_value, exc_tb):
        """
        Defines what the system should do when errors are raised inside the Qt event loop.
        Writes error message with traceback to log file, and end the QtApplication with exit code 1
        This will return control to the 'run' function.
        """
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.master_error_handler('A runtime error was caught - attempting to exit.', tb)
        self._app.exit(1)
