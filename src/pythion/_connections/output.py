from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pythion.connections import Calibration, USBConnection

class Output(ABC):
    """
    Abstract base class for an output device. A derived class is to be made for every type of output,
    and the connection details should be covered in the enter/exit methods.
    Writing values should be internally implemented in the '_write' method, and invoked using the
    'target' property. By default, reading the 'target' property returns the last set target value. Change this
    behaviour to implement feedback by editing the 'target' getter and changing 'has_feedback' to return true.
    """

    _last_set_target: float | None
    _last_set_control: float | None
    _calibration: Calibration

    def __init__(self, *, calibration: Calibration | None = None):
        self._last_set_target = None
        self._last_set_control = None
        self._calibration = Calibration.standard() if calibration is None else calibration
        # TODO: Implement default values

    # __enter__ and __exit__ are only defined to allow subclasses to override them.
    def __enter__(self) -> Output:
        """
        Open connection with device.
        """
        return self
    
    def __exit__(self, *_: Any) -> None:
        """
        Close connections with device.
        """
        pass

    @property
    def target(self) -> float | None:
        return self._last_set_target

    @target.setter
    def target(self, target_value: float) -> None:
        """
        Set a target value for the signal.
        """
        control = self._calibration.to_control(target_value)
        self._last_set_control = control
        self._last_set_target = target_value
        self._write(control) # Important! _write could possibly overwrite the value of _last_set_control and
                             # last_set_target if necessary. It's therefore important to make the _write call
                             # last. 

    @property
    def control(self) -> float | None:
        """
        Note that control is get-only by default - setting the value has to be done by specifying a target value.
        This can of course be changed if needed.
        """
        return self._last_set_control

    @property
    def has_feedback(self) -> bool:
        """
        Returns whether the target property getter provides information about on the output signal value (True),
        or just returns whichever value was last set (False).
        """
        return False
    
    @abstractmethod
    def _write(self, control_signal: float) -> None:
        """
        Actual implementation of writing to device
        """
        pass

# IMPLEMENTATIONS

class MockOutput(Output):
    def _write(self, control_value: float) -> None:
        print(f'Writing control signal value {control_value}')

class PicoOutput(Output):
    """
    Specialization of the Output class for a Pico running a DAC for a voltage supply.
    Target signal is the output voltage of the voltage supply.
    Control signal is a 0-1 float corresponding to minimum/maximum output of the DAC.

    Setting voltage_limit allows for a safety-check if a higher voltage is set.
    Setting a value that's out of bounds for the DAC will result in a maximum/minimum
    signal being sent (provided that the target voltage is safe)
    """
    def __init__(self, port: str, calibration: Calibration, voltage_limit: float | None = None, bits: int = 12):
        self._usb = USBConnection(port)
        self.voltage_limit = voltage_limit
        self.bits = bits
        super().__init__(calibration = calibration)
    
    def __enter__(self) -> PicoOutput:
        self._usb.__enter__()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self._usb.__exit__(*args)
    
    @Output.target.setter # type: ignore
    def target(self, target_value: float) -> None:
        """
        Overwrite the target setter to enforce check that the output target is
         - below safe operating limit
         - within specified range
        """
        if self.voltage_limit is not None and target_value > self.voltage_limit:
            raise ValueError(f'A voltage of {target_value} exceeds the listed DAC capability.')
        control_value = self._calibration.to_control(target_value)
        control_value = max(min(control_value, 1), 0) # Make sure control signal is within range
        self._last_set_control = control_value
        self._last_set_target = self._calibration.to_target(self._last_set_control)
        self._write(control_value)

    def _write(self, control_value: float) -> None:
        """
        Write signal to DAC. control is a float between 0 and 1,
        and will be converted to a binary number.
        """
        binary = round(control_value * (2**self.bits - 1)) # Discretize
        self._usb.write(str(binary))      # Write to usb