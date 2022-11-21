from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.output import Ui_Output
from pythion.connections import Output


class OutputComponent(QWidget, Ui_Output):
    def __init__(self, max_value: int, interface: Output, parent: QWidget | None = None):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.interface = interface
        self.max_value = max_value
        self.configure()

    def configure(self) -> None:
        if self.interface.has_feedback:
            raise NotImplementedError('Outputs with live feedback have not been implemented!')

        # Connect dial to input voltage display
        self.outputDial.setRange(0, self.max_value)
        self.outputSpinbox.setRange(0, self.max_value)
        self.outputDial.valueChanged.connect(self.outputSpinbox.setValue)  # type: ignore
        self.outputSpinbox.valueChanged.connect(self.outputDial.setValue)
        self.setBtn.clicked.connect(self.set_value)  # type: ignore

    def set_value(self) -> None:
        val = self.outputDial.value()
        self.interface.target = val
        self.lastValueLCD.display(val)
