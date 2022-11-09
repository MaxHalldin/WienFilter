from __future__ import annotations
from abc import ABC, abstractmethod
from interfaces.calibration import Calibration

class Output(ABC):
    """
    Abstract base class for an output device. A derived class is to be made for every type of output,
    and the connection details should be covered in the enter/exit methods.
    Writing values should be internally implemented in the '_write' method, and invoked using the
    'target' property. By default, reading the 'target' property returns the last set target value. Change this
    behaviour to implement feedback by editing the 'target' getter and changing 'has_feedback' to return
    true.
    """

    def __init__(self, default: float = None, calibration: Calibration = None) -> None:
        self._last_set = None       # Last set value of TARGET signal
        self._calibration = Calibration.standard() if calibration is None else calibration
        # TODO: Implement default values

    # __enter__ and __exit__ are only defined to allow subclasses to override them.
    @abstractmethod
    def __enter__(self) -> Output:
        """
        Open connection with device.
        """
        pass
    
    @abstractmethod
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