from __future__ import annotations
import time
from pythion._connections.buffer_input import BufferInput
from pythion._connections.usb import USBConnection
from typing import Self, Any
from enum import Enum


class RBDInput(BufferInput, USBConnection):
    class CurrentUnit(Enum):
        NANO = 0
        MICRO = 1
        MILLI = 2

    def __init__(self, *, port: str, rbd_sample_rate: int, pull_rate: int, unit: RBDInput.CurrentUnit):
        self.rbd_sample_rate = rbd_sample_rate

        self.exp = 3  # In case of milliamps; change below if needed
        if unit == self.CurrentUnit.NANO:
            self.exp = 9
        elif unit == self.CurrentUnit.MICRO:
            self.exp = 6

        BAUD_RATE = 57600
        MAX_RESPONSE_SIZE = 25  # Bytes
        BUFFER_CAPACITY = 1020
        if MAX_RESPONSE_SIZE * rbd_sample_rate / pull_rate > BUFFER_CAPACITY:
            print('USB buffer risk overflowing. Increase pull rate or edit USB drivers to increase buffer size')

        BufferInput.__init__(self, pull_rate=pull_rate)
        USBConnection.__init__(self, port=port, baud_rate=BAUD_RATE, eol_char='\r\n')

    def _read_from_device(self) -> list[float]:
        generator = (self.parse_response_string(str) for str in self.read_newlines())

        def check_value(x: float | None):
            return x is not None

        return list(filter(check_value, generator))

    def __enter__(self) -> Self:
        super().__enter__()
        time_interval = round(1000 / self.rbd_sample_rate)  # Interval time in ms
        print(f'{time_interval=}')
        if time_interval <= 0:
            time_interval = 1  # Too high sample rate results in max sampling rate (1 kHz)
        timestr = str(time_interval).rjust(4, '0')
        self.write(f'&I{timestr}')
        return self

    def __exit__(self, *args: Any) -> None:
        self.write('&I0000')
        super().__exit__(*args)

    def parse_response_string(self, message: str) -> float:
        try:
            message = message.strip()
            start = message.index('&')
            message = message[start:]
            assert message[0] == '&' and message[-1] == 'A'
            _, _, value_str, unit_str = message.split(',')
            num = float(value_str)
            exp = self.exp
            prefix = unit_str[0]

            if prefix == "n":
                exp = exp-9
            elif prefix == "m":
                exp = exp-3
            else:
                exp = exp-6
            return num * 10 ** exp
        except (ValueError, AssertionError):
            return None


if __name__ == '__main__':
    ob = RBDInput(port='COM5', rbd_sample_rate=100, pull_rate=1, unit=RBDInput.CurrentUnit.NANO)
    ob.add_input_handler(print)
    ob.start_sampling(5)
    with ob:
        time.sleep(5)
