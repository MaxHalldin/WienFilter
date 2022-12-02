from enum import Enum
from statistics import mean
from time import sleep
import logging

from pythion._routines.routine import Routine
from pythion._gui.output import Output
from pythion._gui.input import Input


logger = logging.getLogger('pythion')


class ValueUpdateSettings(Enum):
    NO_GRAPHICS = 0
    ONLY_LCD = 1
    MOVE_KNOBS = 2


class MeasurementRoutine(Routine):
    def set_output(self, output: Output, value: float, update_settings: ValueUpdateSettings = ValueUpdateSettings.MOVE_KNOBS, block: bool = True) -> None:
        """
        Set the output of a component.
        Parameters:
        output          - the Output instance connected to the hardware we want to set.
        value           - the value to set
        update_settings - one of the following:
            ValueUpdateSettings.NO_GRAPHICS: Write silently to output without affecting the GUI.
                                             If this option is used, the function will return when
                                             a value has been written.
            valueUpdateSettings.ONLY_LCD:    Write to output and update the 'last set target' LCD
                                             display, but without turning the output knobs.
            valueUpdateSettings.MOVE_KNOBS:  Write to output and update both the LCD and the knobs.
        block           - only used when ONLY_LCD or MOVE_KNOBS is selected. Then, block=True means
                          that the function will only return after a value has been written and the
                          GUI has been updated, while block=False allows for the program to continue
                          immediately. This might lead to an unexpected delay in setting the output
                          value if the main thread is being blocked by other things, such as plotting.
        """
        if update_settings == ValueUpdateSettings.NO_GRAPHICS:
            # Bypass the output component and set the value to the hardware interface directly
            interface = output.interface
            interface.target = value
            return
        self.update_widget(output, "set_value", value, block=block)

    def measure(self, input: Input, measuring_time: float):
        interface = input.interface
        interface.restart_buffer()
        # Wait for self.measure_time as many times as needed to recieve at least one measurement
        vals = []
        i = 1
        while True:
            logger.debug(f'GridSearch      measuring ({i})...')
            i = i + 1
            sleep(self.measure_time)
            vals = self.input.clear_buffer()
            if vals:
                break
        average = float(mean(vals))
        logger.debug(f'GridSearch:     measured ({vals}), average {average}.')
        return average
