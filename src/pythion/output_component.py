from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.ui_output import Ui_Output
from pythion.connections import Output


class OutputComponent(QWidget, Ui_Output):
    def __init__(
        self, *,
        max_value: int,
        interface: Output,
        parent: QWidget | None = None,
        name: str | None = None,
        unit: str | None = None
    ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.interface = interface
        self.max_value = max_value
        self.name = name
        self.unit = unit
        self.configure()

    def configure(self) -> None:
        if self.interface.has_feedback:
            raise NotImplementedError('Outputs with live feedback have not been implemented!')

        # Set name label
        namestr = self.name if self.name else 'Output'
        namestr = namestr + (f' [{self.unit}]' if self.unit else '')
        self.nameLabel.setText(namestr)

        # Connect dial and text field to input voltage display
        self.outputDial.setRange(0, self.max_value)
        self.outputSpinbox.setRange(0, self.max_value)
        self.outputDial.valueChanged.connect(self.outputSpinbox.setValue)  # type: ignore
        self.outputSpinbox.valueChanged.connect(self.outputDial.setValue)  # type: ignore
        self.setBtn.clicked.connect(self.set_value)  # type: ignore

    def set_value(self) -> None:
        val = self.outputDial.value()
        self.interface.target = val
        val = self.interface.target  # Outgoing value might have changed due to illegal output
        self.lastValueLCD.display(val)
