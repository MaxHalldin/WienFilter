from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.input import Ui_Input
from pythion.connections import Input


class InputComponent(QWidget, Ui_Input):
    def __init__(
        self, *,
        interface: Input,
        parent: QWidget | None = None,
        name: str | None = None,
        unit: str | None = None
    ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.interface = interface
        self.name = name
        self.unit = unit
        self.configure()

    def configure(self) -> None:
        # Set name label
        namestr = self.name if self.name else 'Output'
        namestr = namestr + (f' [{self.unit}]' if self.unit else '')
        self.nameLabel.setText(namestr)
        self.interface.add_input_handler(self.inputLCD.display)
