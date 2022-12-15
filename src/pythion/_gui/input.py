from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.ui_input import Ui_Input
from pythion._connections.input_interface import InputInterface
from pythion._gui.connect_button import ConnectButton


class Input(QWidget, Ui_Input, ConnectButton):
    def __init__(
        self, *,
        interface: InputInterface,
        rate: int,
        parent: QWidget | None,
        name: str | None = None,
        unit: str | None = None
    ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Initialize connectbutton
        super(Ui_Input, self).__init__()
        # Custom initialization
        self.interface = interface
        self.name = name
        self.unit = unit
        self.rate = rate
        self._value_set = False
        self.configure()

    def configure(self) -> None:
        # Set name label
        label = self.name if self.name else 'Output'
        label = label + (f' [{self.unit}]' if self.unit else '')
        self.label = label
        self.nameLabel.setText(label)
        self.interface.add_input_handler(self._on_new_value)

    def _activate(self):
        self.interface.start_sampling(self.rate)

    def _deactivate(self):
        self._value_set = False
        self.interface.stop_sampling()
        self.inputLCD.setStyleSheet('color: #aaaaaa;')

    def _on_new_value(self, value: float) -> None:
        if not self._value_set:
            self._value_set = True
            self.inputLCD.setStyleSheet('color: #ff0000;')
        self.inputLCD.display(value)

    def __str__(self):
        return self.label
