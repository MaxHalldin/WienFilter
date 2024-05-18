from __future__ import annotations
from enum import Enum
from typing import Self

from srcMAX.pythionMAX._connectionsMAX.output_interfaceMAX import OutputInterface
from srcMAX.pythionMAX._connectionsMAX.usbMAX import USBConnection
from srcMAX.pythionMAX._connectionsMAX.calibrationMAX import Calibration, LinearCalibration


class PowerOptions(Enum):
    VOLTAGE = 0
    CURRENT = 1


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

    def __init__(self,
                 *,
                 port: str | None,
                 control_limit: float | None = None,
                 target_limit: float | None,
                 calibration: Calibration | None = None,
                 mode: PowerOptions = PowerOptions.VOLTAGE
                 ):

        unit = 'V' if mode == PowerOptions.VOLTAGE else 'mA'

        if calibration is None:
            calibration = LinearCalibration(1, unit, unit)

        # Some hard-coded limits for the RS3005P
        if mode == PowerOptions.VOLTAGE and (control_limit is None or control_limit > 30):
            control_limit = 30
        if mode == PowerOptions.CURRENT and (control_limit is None or control_limit > 5000):
            control_limit = 5000

        self._mode = mode

        BAUD_RATE = 9600
        USBConnection.__init__(
            self,
            port=port,
            baud_rate=BAUD_RATE
        )
        OutputInterface.__init__(
            self,
            calibration=calibration,
            control_limit=control_limit,
            target_limit=target_limit
        )

    def __enter__(self) -> Self:
        super().__enter__()
        return self

    @staticmethod
    def _to_voltage_string(voltage: float) -> str:
        return f'{voltage:.2f}'.rjust(5, '0')

    @staticmethod
    def _to_current_string(current: float) -> str:
        return f'{(current / 1000):.3f}'

    def _write(self, control_value: float) -> None:
        is_voltage = self._mode == PowerOptions.VOLTAGE
        if is_voltage:
            str = self._to_voltage_string(control_value)
        else:
            str = self._to_current_string(control_value)
        self.write(f'{"V" if is_voltage else "I"}SET1:{str}')
