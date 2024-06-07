from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Self, Tuple
import logging

from srcMAX.pythionMAX._connectionsMAX.calibrationMAX import Calibration


logger = logging.getLogger('pythion')


class Limits:
    def __init__(self, min: float | None, max: float | None):
        self.min = min
        self.max = max

    def check(self, value: float) -> bool:
        return (self.min is None or self.min < value) and (self.max is None or self.max > value)

    def correct(self, value) -> tuple[float, bool]:
        """
        Returns is_valid, new_value
        if is_valid, then new_value must equal value
        """
        if self.min is not None and value < self.min:
            return False, self.min
        if self.max is not None and value > self.max:
            return False, self.max
        return True, value


class OutputInterface(ABC):
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
    _on_invalid_output: list[Callable[[], None]]

    def __init__(self,
                 *,
                 calibration: Calibration | None = None,
                 target_limit: float | None = None,
                 control_limit: float | None = None,
                 target_minimum: float | None = None,
                 control_minimum: float | None = None):
        self._last_set_target = None
        self._last_set_control = None
        self._calibration = Calibration.standard() if calibration is None else calibration
        self.target_limits = Limits(target_minimum, target_limit)
        self.control_limits = Limits(control_minimum, control_limit)
        self._on_invalid_output = []

    # __enter__ and __exit__ are defined since most Outputs require IO handling, and it's
    # nice if all Outputs then accept the use of context managers. However, to avoid masking
    # __enter__/__exit__ calls to classes higher in the mro, the call is passed forward to super()
    def __enter__(self) -> Self:
        try:
            super().__enter__()  # type: ignore
        except AttributeError:
            pass
        return self

    def __exit__(self, *args: Any) -> None:
        try:
            super().__exit__(*args)  # type: ignore
        except AttributeError:
            pass

    @property
    def target(self) -> float | None:
        return self._last_set_target

    @target.setter
    def target(self, target_value: float) -> None:
        """
        Set a target value for the signal.
        """
        control_value = self._calibration.to_control(target_value)
        is_valid, new_target, new_control = self._validate(target_value, control_value)
        if not is_valid:
            for handler in self._on_invalid_output:
                handler()
        self._last_set_control = new_control
        self._last_set_target = new_target
        self._write(new_control)

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

    def add_invalid_output_handler(self, handler: Callable[[], None]) -> None:
        self._on_invalid_output.append(handler)

    @abstractmethod
    def _write(self, control_signal: float) -> None:
        """
        Actual implementation of writing to device
        """
        pass

    @abstractmethod
    def _read_from_device(self) -> list[float, str]:
        """
        Actual implementation of reading from device
        """
        pass

    def _validate(self, target_signal: float, control_signal: float) -> Tuple[bool, float, float]:
        """
        Returns (isValid, new_target, new_control)
        if isValid, then new_target and new_control must remain unchanged.
        """
        target_valid, target_signal = self.target_limits.correct(target_signal)
        if not target_valid:
            logger.debug('OutputInterface: Invalid target set. Adjusting...')
            control_signal = self._calibration.to_control(target_signal)
        control_valid, control_signal = self.control_limits.correct(control_signal)
        if not control_valid:
            logger.debug('OutputInterface: Invalid control set. Adjusting...')
            target_signal = self._calibration.to_target(control_signal)
            if not self.target_limits.check(target_signal):
                logger.error('OutputInterface: Cannot find any allowed output signal value.')
        # After this point, both target_signal and control_signal should be within bounds.
        return (target_valid and control_valid), target_signal, control_signal

# IMPLEMENTATIONS

class MockOutput(OutputInterface):
    def _write(self, control_value: float) -> None:
        # print(f'Writing control signal value {control_value}')
        logger.debug(f'MockOutput:     Setting control_signal to {control_value}')
    
    def _read_from_device(self) -> None:
        pass
    