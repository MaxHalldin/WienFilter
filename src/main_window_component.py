from __future__ import annotations
from layout.main_window import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from interfaces.output import Output

class MainWindowComponent(QMainWindow, Ui_MainWindow):
    def __init__(self, *children, parent=None):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)
        # Custom initialization
    
    def add_children(self, *children) -> None:
        for child in children:
            self.mainLayout.addWidget(child)
            