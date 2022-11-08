from __future__ import annotations
from abc import ABC, abstractmethod

class Calibration(ABC):
    """
    This is a base class for the relations between a target signal and a control signal of an input or output device.
    """
    def __init__(self, control_unit: str = None, target_unit: str = None) -> None:
        self.control_unit = control_unit # Units for control signal
        self.target_unit = target_unit   # Units for target signal

    @abstractmethod
    def to_target(self, control_value: float) -> float:
        """
        Turn control value to target value, for example used to read from input devices.
        """
        pass

    @abstractmethod
    def to_control(self, target_value: float) -> float:
        """
        Turn target value to control value, for example used to write to output devices.
        """
        pass

    @staticmethod
    def standard(unit: str = None) -> LinearOutputCalibration:
        """
        Factory method for the trivial relation (control=target). Specify only unit of both signals.
        """
        return LinearOutputCalibration(1, unit, unit)

class LinearCalibration(Calibration):
    """
    Describes a linear relationship between control- and target signals.
    """
    def __init__(self, prop: float, control_unit: str = None, target_unit: str = None) -> None:
        """
        Prop: constant of proportionality, i.e. target = control * prop
        """
        self._prop = prop
        super().__init__(control_unit, target_unit)
    
    def to_target(self, control_value: float) -> float:
        return control_value * self._prop

    def to_control(self, target_value: float) -> float:
        return target_value / self._prop

# TODO: IMPLEMENT INTERPOLATION-BASED CALIBRATION