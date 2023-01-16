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
    label: str

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
        label = name if name else 'Output'
        self.label = label + (f' [{unit}]' if unit else '')
        self.configure()

    def configure(self) -> None:
        if self.interface.has_feedback:
            logger.warning('Output:         Live feedback has not been implemented!')

        # Set name label
        self.nameLabel.setText(self.label)

        # Connect dial and text field to input voltage display
        self.outputDial.setRange(0, self.max_value)
        self.outputSpinbox.setRange(0, self.max_value)
        self.outputDial.valueChanged.connect(self.outputSpinbox.setValue)  # type: ignore
        self.outputSpinbox.valueChanged.connect(self.outputDial.setValue)  # type: ignore
        self.setBtn.clicked.connect(self._on_setvalue_pressed)  # type: ignore

    def _on_setvalue_pressed(self) -> None:
        self.set_value_and_update(self.outputDial.value())

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

    def _set_value_without_graphics(self, val: float):
        """
        This method *only* sets the underlying hardware interface value.
        It's used by other set_value methods, but it can inprinciple also
        be used by external callers. Beware, however, that there will be no
        visual indication that the output value has changed!
        """
        logger.debug(f'Output:         Setting {self.label} to {val}.')
        self.interface.target = val  # Try to set value on the underlying interface

    def _update_graphics(self):
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

    def set_value_and_update(self, val: float) -> None:
        self._set_value_without_graphics(val)
        self._update_graphics()

    def __str__(self):
        return self.label

    @pyqtSlot(int, bool)
    def set_value(self, val: int, move_knobs: bool = True) -> None:
        """
        External method that can be invoked to change the output value and possibly move the knobs accordingly.
        Note that even when move_knobs is False, the 'last set target signal' LCD will still change, so
        there's no way of setting the value directly without changing the graphics by any of this component's methods.
        If you want to achieve this, for example due to performance reasons, then adress the hardware interface (i.e.
        the OutputInterface derivative) directly. Afterwards, you can call the delayed_set_value method to update the graphics
        when time is available.
        """
        if not self._connected:
            logger.warning('Output:         Attempted to set value without connection')
            return
        # Change value just like the user would:
        if move_knobs:
            self.outputDial.setValue(val)  # TODO: support float values for output
        self.set_value_and_update(val)

    @pyqtSlot(int, bool)
    def delayed_set_value(self, val: int, move_knobs: bool = True):
        """
        This method can be called if the underlying device's target value has *already* been set remotely (for example,
        to set the value instantaniously without having to wait for a slot on the main thread).

        This method only updates the graphics, i.e. no value is actually set
        """
        if move_knobs:
            self.outputDial.setValue(val)
        self._update_graphics()

    def __exit__(self, *args):
        if self.zeroOnDisconnectBox.isChecked() and self._connected:
            self.set_value(0, True)
        super().__exit__(self, *args)
