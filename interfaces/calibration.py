from abc import ABC, abstractmethod

class Calibration(ABC):
    """
    This is a base class for the relations between a control signal and a target signal of an input or output device.
    """
    def __init__(self, control_unit: str, target_unit: str):
        self.control_unit = control_unit # Units for control signal
        self.target_unit = target_unit   # Units for target signal
    
    @abstractmethod
    def convert(self, control_value: float) -> float:
        """
        Turn control value to target value
        """
        pass

class LinearCalibration(Calibration):
    """
    Describes a linear relationship between control- and target signals.
    """
    def __init__(self, control_unit: str, target_unit: str, prop: float):
        """
        Prop: constant of proportionality.
        """
        self._prop = prop
        super().__init__(control_unit, target_unit)
    
    def convert(self, control_value):
        return control_value * self._prop

# TODO: IMPLEMENT INTERPOLATION-BASED CALIBRATION