from pythion._connections.buffer_input import BufferInput
from pythion._connections.usb import USBConnection


class RBDInput(BufferInput, USBConnection):
    def __init__(self, port: str, rbd_sample_rate: int, pull_rate: int, refresh_rate: int):
        BAUD_RATE = 57600
        MAX_RESPONSE_SIZE = 25  # Bytes
        BUFFER_CAPACITY = 1020
        if MAX_RESPONSE_SIZE * rbd_sample_rate / pull_rate > BUFFER_CAPACITY:
            print('USB buffer risk overflowing. Increase pull rate or edit USB drivers to increase buffer size')
        BufferInput.__init__(self)
        USBConnection.__init__(self, port=port, baud_rate=BAUD_RATE, add_line_break=True)

    def _read_from_device(self) -> list[float]:
        return [float(str.strip()) for str in self.read_newlines()]

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
