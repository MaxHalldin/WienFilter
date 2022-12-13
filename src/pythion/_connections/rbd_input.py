from __future__ import annotations
import time
import re
import logging
from pythion._connections.buffer_input import BufferInput
from pythion._connections.usb import USBConnection
from typing import Self, Any, TypeGuard
from enum import Enum


logger = logging.getLogger('pythion')


class RBDInput(BufferInput, USBConnection):
    class CurrentUnit(Enum):
        NANO = 0
        MICRO = 1
        MILLI = 2

    exp: int

    def __init__(self, *, port: str, rbd_sample_rate: int, pull_rate: int, unit: RBDInput.CurrentUnit, discard_unstable: bool = True):
        self.rbd_sample_rate = rbd_sample_rate
        self.discard_unstable = discard_unstable
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

        def check_value(x: float | None) -> TypeGuard[float]:
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

    def parse_response_string(self, message: str) -> float | None:
        try:
            original_message = message.strip()
            if not re.match(r'^&S[=<>*],Range=\d{3}[num]A,[+-][\d.]{6},[mun]A$', original_message).bool():
                logging.warning(f"RBDInput:       Cannot interpret the line '{original_message}' as it doesn't fit pattern.")
            if self.discard_unstable:
                if original_message[2] == '*':
                    return None
                match original_message[2]:
                    case '*':
                        logging.warning('RBDInput:       Recieved unstable measurement, discarding...')
                        return None
                    case '>' | '<':
                        logging.warning('RBDInput:       Measurement outside of range, discarding...')
                        return None

            _, _, value_str, unit_str = original_message.split(',')
            num = float(value_str)
            exp = self.exp

            match unit_str[0]:
                case 'n':
                    exp = exp-9
                case 'u':
                    exp = exp-6
                case 'm':
                    exp = exp-3
            res: float = num * 10 ** exp
            logger.debug(f'RBDInput:       Interpreted {original_message} as {res}')
            return res

        except (ValueError, AssertionError):
            logging.warning(f"RBDInput:       Unexpected error when the line '{message.strip()}' was parsed.")
            return None


if __name__ == '__main__':
    ob = RBDInput(port='COM5', rbd_sample_rate=100, pull_rate=1, unit=RBDInput.CurrentUnit.NANO)
    ob.add_input_handler(print)
    ob.start_sampling(5)
    with ob:
        time.sleep(5)
