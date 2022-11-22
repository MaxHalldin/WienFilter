from pythion._connections.buffer_input import BufferInput
from pythion._connections.usb import USBConnection
from typing import Self, Any


class RBDInput(BufferInput, USBConnection):
    def __init__(self, *, port: str, rbd_sample_rate: int, pull_rate: int):
        self.rbd_sample_rate = rbd_sample_rate

        BAUD_RATE = 57600
        MAX_RESPONSE_SIZE = 25  # Bytes
        BUFFER_CAPACITY = 1020
        if MAX_RESPONSE_SIZE * rbd_sample_rate / pull_rate > BUFFER_CAPACITY:
            print('USB buffer risk overflowing. Increase pull rate or edit USB drivers to increase buffer size')

        BufferInput.__init__(self, pull_rate=pull_rate)
        USBConnection.__init__(self, port=port, baud_rate=BAUD_RATE, eol_char='\r\n')

    def _read_from_device(self) -> list[float]:
        return [float(str.strip()) for str in self.read_newlines()]

    def __enter__(self) -> Self:
        super().__enter__()
        time_interval = round(1000 / self.rbd_sample_rate)  # Interval time in ms
        if time_interval <= 0:
            time_interval = 1  # Too high sample rate results in max sampling rate (1 kHz)
        timestr = str(time_interval).rjust(4, '0')
        print(f'&I{timestr}')
        #  self.write(timestr)
        return self

    def __exit__(self, *args: Any) -> None:
        self.write('&I0000')
        super().__exit__(*args)

    @staticmethod
    def parse_response_string(message: str) -> float:
        start = message.index('&')
        num = float(message[10+start:20+start])
        unit = message[21]
        mult = 1
        if unit == "n":
            pass
        elif unit == "m":
            mult = 10**6
        else:
            mult = 10**3
        return num * mult
