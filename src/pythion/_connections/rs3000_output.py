from __future__ import annotations
from enum import Enum
from typing import Self
import time

from pythion._connections.output import OutputInterface
from pythion._connections.usb import USBConnection
from pythion._connections.calibration import Calibration, LinearCalibration


class RS3000Output(OutputInterface, USBConnection):
    """
    Specialization of the Output class for a RS3005P power supply.
    Control and target signal is the output voltage of the voltage supply.
    PARAMETERS:
        port: str                                   - The port to use, like "COM#"
        voltage_limit   : float | None              - Maximum allowed voltage (in V)
        current_limit   : float | None              - Maximum allowed current (in mA)
        calibration     : Calibration               - Relationship between control signal and target signal.
                                                      Given by a pythion.connections.Calibration object.
        mode            : RS3000Output.PowerOption  - Determines whether voltage [V] or current [mA] will
                                                      be used as target signal.
    """
    class PowerOptions(Enum):
        VOLTAGE = 0
        CURRENT = 1

    def __init__(self,
                 *,
                 port: str | None,
                 voltage_limit: float | None = None,
                 current_limit: float | None = None,
                 calibration: Calibration | None = None,
                 mode: PowerOptions = PowerOptions.VOLTAGE
                 ):

        unit = 'V' if mode == self.PowerOptions.VOLTAGE else 'mA'

        if calibration is None:
            calibration = LinearCalibration(1, unit, unit)

        # Some hard-coded limits for the RS3005P
        if voltage_limit is None or voltage_limit > 30:
            voltage_limit = 30
        if current_limit is None or current_limit > 5000:
            current_limit = 5000

        self._mode = mode
        self._voltage_limit = voltage_limit
        self._current_limit = current_limit
        target_limit = voltage_limit if mode == self.PowerOptions.VOLTAGE else current_limit

        BAUD_RATE = 9600
        USBConnection.__init__(
            self,
            port=port,
            baud_rate=BAUD_RATE
        )
        OutputInterface.__init__(
            self,
            calibration=calibration,
            target_limit=target_limit
        )

    def __enter__(self) -> Self:
        super().__enter__()
        self._initial_config()
        return self

    @staticmethod
    def _to_voltage_string(voltage: float) -> str:
        return f'{voltage:.2f}'.rjust(5, '0')

    @staticmethod
    def _to_current_string(current: float) -> str:
        return f'{(current / 1000):.3f}'

    def _initial_config(self) -> None:
        if self._mode == self.PowerOptions.VOLTAGE:
            self.write(f'ISET1:{self._to_current_string(self._current_limit)}')
        else:
            self.write(f'VSET1:{self._to_voltage_string(self._voltage_limit)}')

    def _write(self, control_value: float) -> None:
        is_voltage = self._mode == self.PowerOptions.VOLTAGE
        if is_voltage:
            str = self._to_voltage_string(control_value)
        else:
            str = self._to_current_string(control_value)
        self.write(f'{"V" if is_voltage else "I"}SET1:{str}')
