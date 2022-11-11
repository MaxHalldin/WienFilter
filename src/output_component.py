from __future__ import annotations
from layout.output import Ui_Output
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from interfaces.output import Output

class OutputComponent(QMainWindow, Ui_Output):
    def __init__(self, max_value: int, interface: Output, parent=None):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)
        # Custom initialization
        self.interface = interface
        self.max_value = max_value
        self.configure()

    def configure(self) -> None:
        if self.interface.has_feedback:
            raise NotImplementedError('Outputs with live feedback have not been implemented!')
        
        # Connect dial to input voltage display
        self.voltageDial.setRange(0, self.max_value)
        self.voltageDial.valueChanged.connect(self.newValueLCD.display)
        self.setBtn.clicked.connect(self.set_value)
    
    def set_value(self) -> None:
        val = self.voltageDial.value()
        self.interface.target = val
        self.lastValueLCD.display(val)