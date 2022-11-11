from __future__ import annotations
from abc import ABC, abstractmethod
from interfaces.calibration import Calibration, LinearCalibration
from interfaces.usb import USBConnection

class Output(ABC):
    """
    Abstract base class for an output device. A derived class is to be made for every type of output,
    and the connection details should be covered in the enter/exit methods.
    Writing values should be internally implemented in the '_write' method, and invoked using the
    'target' property. By default, reading the 'target' property returns the last set target value. Change this
    behaviour to implement feedback by editing the 'target' getter and changing 'has_feedback' to return
    true.
    """

    def __init__(self, *, calibration: Calibration = None) -> None:
        self._last_set = None       # Last set value of TARGET signal
        self._calibration = Calibration.standard() if calibration is None else calibration
        # TODO: Implement default values

    # __enter__ and __exit__ are only defined to allow subclasses to override them.
    def __enter__(self) -> Output:
        """
        Open connection with device.
        """
        pass
    
    def __exit__(self, *_) -> None:
        """
        Close connections with device.
        """
        pass

    @property
    def target(self) -> float:
        """
        Getter for the 'target' property. Returns last set target value, by default
        """
        return self._last_set

    @target.setter
    def target(self, value: float) -> None:
        """
        Set a target value for the signal.
        """
        self._write(self._calibration.to_control(value))
        self._last_set = value

    @property
    def control(self) -> float:
        """
        Returns the last set control signal, by default
        """
        return self._calibration.to_control(self._last_set)

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
    def _write(self, control_value) -> None:
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
    def __init__(self, port: str, calibration: Calibration, voltage_limit: float = None, bits = 12):
        self._usb = USBConnection(port)
        self.voltage_limit = voltage_limit
        self.bits = bits
        self._last_control = None # Use this local variable to overwrite control signal getter,
                                  # as this might differ if value is out of DAC range.
        super().__init__(calibration = calibration)
    
    def __enter__(self):
        self._usb.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        self._usb.__exit__(exc_type, exc_value, tb)
    
    @Output.target.setter
    def target(self, value: float):
        if self.voltage_limit is not None and value > self.voltage_limit:
            raise ValueError(f'A voltage of {value} exceeds the listed DAC capability.')
        Output.target.fset(self, value)
    
    @Output.control.getter
    def control(self):
        return self._last_control

    def _write(self, control: float) -> None:
        """
        Write signal to DAC. control is a float between 0 and 1,
        and will be converted to a binary number.
        """
        control = max(min(control, 1), 0) # Make sure control signal is within range
        self._last_control = control
        binary = round(control * (2**self.bits - 1)) # Discretize
        self._usb.write(str(binary))      # Write to usb