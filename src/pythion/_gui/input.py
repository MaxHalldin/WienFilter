from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.ui_input import Ui_Input
from pythion._connections.input import InputInterface
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
        self._connected = False
        self._in_context_manager = False
        self.configure()

    def configure(self) -> None:
        # Set name label
        namestr = self.name if self.name else 'Output'
        namestr = namestr + (f' [{self.unit}]' if self.unit else '')
        self.nameLabel.setText(namestr)
        self.interface.add_input_handler(self.inputLCD.display)

    def _activate(self):
        self.interface.start_sampling(self.rate)

    def _deactivate(self):
        self.interface.stop_sampling()
