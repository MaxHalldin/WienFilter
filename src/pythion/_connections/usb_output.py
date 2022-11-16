from __future__ import annotations
from typing import Any, Self
from abc import ABC

from pythion._connections.output import Output
from pythion._connections.calibration import Calibration
from pythion._connections.usb import USBConnection


class USBOutput(Output, ABC):
    """
    Partial specialization of the Output class for output devices that use a USB connection.
    The class governs setup, opening and closing of a USB port connection.
    """
    def __init__(self, *, port: str, baud_rate: int, calibration: Calibration | None, target_limit: float | None = None, add_line_break: bool = False):
        self._usb = USBConnection(port, baud_rate, add_line_break)
        super().__init__(calibration=calibration, target_limit=target_limit)

    def __enter__(self) -> Self:
        self._usb.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._usb.__exit__(*args)
