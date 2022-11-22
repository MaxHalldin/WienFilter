from __future__ import annotations
from PyQt5.QtWidgets import QWidget

from pythion._layout.ui_output import Ui_Output
from pythion.connections import OutputInterface


class Output(QWidget, Ui_Output):
    def __init__(
        self, *,
        max_value: int,
        interface: OutputInterface,
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
        self.setBtn.clicked.connect(self._on_button_pressed)  # type: ignore

    def _on_button_pressed(self) -> None:
        self._set_value(self.outputDial.value())

    def _set_value(self, val: float) -> None:
        self.interface.target = val  # Try to set value on the underlying interface
        val = self.interface.target  # Outgoing value might have changed due to illegal output, so get back the set value
        self.lastValueLCD.display(val)  # Make sure that the knobs are able to set this value!

    def set_value(self, val: float, move_knobs: bool = False) -> None:
        """
        External method that can be invoked to change the output value.
        If move_knobs is true, the graphical knobs will also move to the
        corresponding output value.
        """
        if move_knobs:
            # Change value just like the user would:
            self.outputDial.setValue(val)
            self._on_button_pressed()
        else:
            # Change value "silently"
            self._set_value(val)
