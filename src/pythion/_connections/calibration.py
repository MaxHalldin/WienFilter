from __future__ import annotations
# from typing import Callable
from typing import Self
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np


class Calibration(ABC):
    """
    This is a base class for the relations between a target signal and a control signal of an input or output device.
    """
    def __init__(self, control_unit: str | None = None, target_unit: str | None = None) -> None:
        self.control_unit = control_unit  # Units for control signal
        self.target_unit = target_unit    # Units for target signal

    def plot(self, min_target: float, max_target: float, samples: int):
        xx = np.linspace(min_target, max_target, samples)
        yy = [self.to_control(x) for x in xx]
        plt.plot(xx, yy)
        plt.xlabel('Target Signal' + (f' [{self.target_unit}]' if self.target_unit is not None else ''))
        plt.ylabel('Required Control Signal' + (f' [{self.control_unit}]' if self.control_unit is not None else ''))
        plt.show()

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
    def standard(unit: str | None = None) -> LinearCalibration:
        """
        Factory method for the trivial relation (control=target). Specify only unit of both signals.
        """
        return LinearCalibration(1, unit, unit)


class LinearCalibration(Calibration):
    """
    Describes a linear relationship between control- and target signals.
    """
    def __init__(self, prop: float, control_unit: str | None = None, target_unit: str | None = None) -> None:
        """
        Prop: constant of proportionality, i.e. target = control * prop
        """
        self._prop = prop
        super().__init__(control_unit, target_unit)

    def to_target(self, control_value: float) -> float:
        return control_value * self._prop

    def to_control(self, target_value: float) -> float:
        return target_value / self._prop


class InterpolCalibration(Calibration):
    def __init__(
        self,
        points: list[tuple[float, float]],
        extrapolate: bool = False,
        target_unit: str | None = None,
        control_unit: str | None = None
    ):
        """
        Initialize InterpolCalibration object.
        points is a list of (target_value, control_value) tuples.
        If extrapolate is set to true, the outmost line at the end of the interval
        will be used to extrapolate the trend beyond the valid calibration domain.
        """
        # Sort on first index
        self.points = sorted(points)

        # Check that list is valid:
        if len(points) < 2:
            raise ValueError("Calibration requires at least 2 points")

        last_target: float | None = None
        last_control: float | None = None

        for target, control in self.points:
            if last_target is not None:
                assert last_control is not None
                if last_control >= control or last_target == target:
                    raise ValueError('Invalid calibration. Points must form a strictly increasing function.')
            last_target, last_control = target, control

        self.extrapolate = extrapolate
        super().__init__(control_unit, target_unit)

    def to_control(self, target_value: float) -> float:
        return self._linear_interpolation(target_value, False)

    def to_target(self, control_value: float) -> float:
        return self._linear_interpolation(control_value, True)

    def auto_plot(self) -> None:
        super().plot(self.points[0][0], self.points[-1][0], 1000)

    def _linear_interpolation(self, x_value: float, flip_xy: bool = False) -> float:
        def get_xy(i: int) -> tuple[float, float]:
            x, y = self.points[i]
            if flip_xy:
                return y, x
            return x, y

        # Enumerate over index because get_xy will be used to get elements
        for i in range(len(self.points)):
            x, y = get_xy(i)
            if x_value < x:
                # x_value is in between x[i-1] and x[i]!
                if i > 0:
                    prev_x, prev_y = get_xy(i-1)
                    return (x_value-prev_x) / (x-prev_x) * (y-prev_y) + prev_y
                else:
                    if not self.extrapolate:
                        raise ValueError('Set value is out of bounds for the calibration domain. Set extrapolate to True if you wish to continue.')
                    next_x, next_y = get_xy(i+1)
                    return (x_value-x) / (next_x-x) * (next_y-y) + y
        # Apparently, x_value >= x[-1]
        x1, y1 = get_xy(-2)  # Next to last
        x2, y2 = get_xy(-1)  # Last
        if not self.extrapolate and x_value != x2:
            raise ValueError('Set value is out of bounds for the calibration domain. Set extrapolate to True if you wish to continue.')
        return (x_value-x1) / (x2-x1) * (y2-y1) + y1

    @classmethod
    def from_file(
            cls,
            filename: str,
            extrapolate: bool = False,
            target_unit: str | None = None,
            control_unit: str | None = None
    ) -> Self:
        """
        Assuming csv-like file with comma-separated values and decimal point.
        Ordered like (target, control), with one point per row.
        """
        with open(filename) as file:
            points = [(float(s1), float(s2)) for s1, s2 in map(lambda s: s.strip().split(','), file.readlines())]
            return cls(points, extrapolate, target_unit, control_unit)


def main() -> None:
    InterpolCalibration.from_file("testcal.csv", False, 'mA', 'mA').auto_plot()


if __name__ == '__main__':
    main()
