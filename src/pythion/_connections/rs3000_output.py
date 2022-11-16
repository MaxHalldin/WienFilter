from __future__ import annotations

from pythion._connections.usb_output import USBOutput
from pythion._connections.calibration import Calibration, LinearCalibration


class RS3000Output(USBOutput):
    """
    Specialization of the Output class for a RS3005P power supply.
    Control and target signal is the output voltage of the voltage supply.

    Setting voltage_limit allows for a safety-check if a higher voltage is set.
    Setting a value that's out of bounds will result in a maximum/minimum
    signal being sent
    """
    def __init__(self, *, port: str, voltage_limit: float | None = None, calibration: Calibration | None = None):
        if calibration is None:
            calibration = LinearCalibration(1, 'V', 'V')
        if voltage_limit is None or voltage_limit > 30:
            voltage_limit = 30
        BAUD_RATE = 9600
        super().__init__(port=port, baud_rate=BAUD_RATE, calibration=calibration, target_limit=voltage_limit)

    def _write(self, control_value: float) -> None:
        val = round(control_value)
        val_str = str(val).rjust(2, '0')
        self._usb.write(f'VSET1:{val_str}.00')
