from __future__ import annotations
import logging
import time

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from pythion._layout.ui_output import Ui_Output
from pythion._connections.output_interface import OutputInterface
from pythion._gui.connect_button import ConnectButton

logger = logging.getLogger('pythion')


class Output(QWidget, Ui_Output, ConnectButton):
    valueChanged: pyqtSignal = pyqtSignal(float)
    namestr: str

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
        # ConnectButton initialization
        super(Ui_Output, self).__init__()
        # Custom initialization
        self.interface = interface
        self.max_value = max_value
        self.name = name
        self.unit = unit
        self._value_set = False
        namestr = name if name else 'Output'
        self.namestr = namestr + (f' [{unit}]' if unit else '')
        self.configure()

    def configure(self) -> None:
        if self.interface.has_feedback:
            logger.warning('Output:         Live feedback has not been implemented!')

        # Set name label
        self.nameLabel.setText(self.namestr)

        # Connect dial and text field to input voltage display
        self.outputDial.setRange(0, self.max_value)
        self.outputSpinbox.setRange(0, self.max_value)
        self.outputDial.valueChanged.connect(self.outputSpinbox.setValue)  # type: ignore
        self.outputSpinbox.valueChanged.connect(self.outputDial.setValue)  # type: ignore
        self.setBtn.clicked.connect(self._on_setvalue_pressed)  # type: ignore

    def _on_setvalue_pressed(self) -> None:
        self._set_value(self.outputDial.value())

    def _activate(self) -> None:
        """
        Called just after output connection has been established
        """
        if self.zeroOnConnectBox.isChecked():
            time.sleep(0.1)
            self.set_value(0, True)
        self.outputDial.setEnabled(True)
        self.outputSpinbox.setEnabled(True)
        self.setBtn.setEnabled(True)

    def _deactivate(self) -> None:
        """
        Called just before output connection is destroyed
        """
        if self.zeroOnDisconnectBox.isChecked():
            self.set_value(0, True)
        self.lastValueLCD.setStyleSheet('color: #aaaaaa;')
        self.outputDial.setDisabled(True)
        self.outputSpinbox.setEnabled(True)
        self.setBtn.setDisabled(True)

    def _select_port_and_retry(self) -> None:
        assert self._in_context_manager
        raise NotImplementedError('No port selection gui has been made yet!')

    def _set_value(self, val: float) -> None:
        logger.debug(f'Output:         Setting {self.namestr} to {val}.')
        self.interface.target = val  # Try to set value on the underlying interface
        val = self.interface.target  # Outgoing value might have changed due to illegal output, so get back the set value
        if not self._value_set:
            # If this is the first value that's been set, "activate" LCD
            self._value_set = True
            self.lastValueLCD.setStyleSheet('color: #ff0000')
        changed = False
        if self.lastValueLCD.value() != val:
            changed = True
        self.lastValueLCD.display(val)
        if changed:
            self.valueChanged.emit(val)

    @pyqtSlot(int, bool)
    def set_value(self, val: int, move_knobs: bool) -> None:
        """
        External method that can be invoked to change the output value.
        If move_knobs is true, the graphical knobs will also move to the
        corresponding output value.
        """
        if not self._connected:
            logger.warning('Output:         Attempted to set value without connection')
            return
        if move_knobs:
            # Change value just like the user would:
            self.outputDial.setValue(val)  # TODO: support float values for output
            self._on_setvalue_pressed()
        else:
            # Change value "silently"
            self._set_value(val)
