from __future__ import annotations

from typing import Tuple
from pythion._connections.calibration import Calibration
from pythion._connections.output import Output
from pythion._connections.usb import USBConnection


class PicoOutput(Output, USBConnection):
    """
    Specialization of the Output class for a Pico running a DAC for a voltage supply.
    Target signal is the output voltage of the voltage supply.
    Control signal is a 0-1 float corresponding to minimum/maximum output of the DAC.

    Setting voltage_limit allows for a safety-check if a higher voltage is set.
    Setting a value that's out of bounds for the DAC will result in a maximum/minimum
    signal being sent (provided that the target voltage is safe)
    """
    def __init__(self, *, port: str, calibration: Calibration, voltage_limit: float | None = None, bits: int = 12):
        self.bits = bits
        BAUD_RATE = 115200
        # Initialize USB Connection
        USBConnection.__init__(
            self,
            port=port,
            baud_rate=BAUD_RATE,
            eol_char='\n'
        )
        # Initialize the output parent class
        Output.__init__(
            self,
            calibration=calibration,
            target_limit=voltage_limit
        )

    def _write(self, control_value: float) -> None:
        """
        Write signal to DAC. control is a float between 0 and 1,
        and will be converted to a binary number.
        """
        binary = round(control_value * (2**self.bits - 1))  # Discretize
        self.write(str(binary))      # Write to usb

    def _validate(self, target_value: float, control_value: float) -> Tuple[bool, float, float]:
        # Not only must output voltage be safe (super()._validate(...)),
        # The control signal must also be between 0 and 1.

        # Check parent validation (if target value is safe)
        parent_valid, target_value, control_value = super()._validate(target_value, control_value)
        changed = False
        if control_value < 0:
            changed = True
            control_value = 0
        if control_value > 1:
            changed = True
            control_value = 1
        if changed:
            target_value = self._calibration.to_target(control_value)
            # Parent must be re-validated:
            control_validation, _, _ = super()._validate(target_value, control_value)
            if not control_validation:
                raise ValueError('No valid output could be set with the current configuration')
        return parent_valid and not changed, target_value, control_value


PicoOutput(port='COM3', calibration=Calibration.standard())
