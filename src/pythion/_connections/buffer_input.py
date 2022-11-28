from pythion._connections.input import TimerInput
from pythion._connections.usb import USBConnection
from threading import Timer
from math import floor
import time
from typing import Self, Any
from abc import abstractmethod


class BufferInput(TimerInput):
    """
    The abstract BufferInput class extends the ordinary Input class (thruogh TimerInput),
    and provides one major new feature for the subclasses to implement: sampling data at a different
    rate than what's presented to the user interface. For example, a sample rate of 1 Hz might be
    enough to update the GUI reading, but numerical computations such as integrating a current could
    require many more data points.

    The BufferInput seeks to solve this by reading input in chunks from an input buffer, such as a
    USB stream. Depending on operating mode, old data is either cached internally or overwritten as
    new data arrives (buffer=False means overwrite). The TimerInput timer is used for pushing the
    latest data to the user at a regular interval. Meanwhile, an internal timer is also used to pull
    data from the device <pull_rate> times per second. Setting pull_rate to None means the device will
    be read whenever a new value needs to be pushed. Set the pull rate higher than the push rate to
    avoid overflow in the hardware buffer.

    To implement the class, implement the method _read_from_device that reads data from the underlying
    data buffer and returns the result as a list of floats.
    """
    _buffer: list[float] | None
    _latest: float
    _pull_timer: Timer | None
    _pull_wait_time: float

    def __init__(self, *, buffer: bool = False, pull_rate: int | None = None, pull_on_buffer_read: bool = True):
        self._buffer = [] if buffer else None
        self._latest = 0
        self.pull_on_buffer_read = pull_on_buffer_read
        super().__init__()

        self._pull_timer = None
        if pull_rate is not None:
            self._pull_wait_time = 1 / pull_rate
            self._pull_timer = Timer(self._pull_wait_time, self._pull_callback)

    def __enter__(self) -> Self:
        super().__enter__()
        if self._pull_timer is not None:
            self._pull_timer.start()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._pull_timer is not None:
            self._pull_timer.cancel()
        super().__exit__(*args)

    def _update_buffer(self) -> None:
        data = self._read_from_device()
        if self._buffer is not None:
            self._buffer.extend(data)
        if data:
            self._latest = data[-1]

    def _read(self) -> float:
        if self._pull_timer is None:  # We need to read from device manually
            self._update_buffer()
        return self._latest

    def _start_pull_timer(self) -> None:
        self._pull_timer = Timer(self._pull_wait_time, self._pull_callback)
        self._pull_timer.start()

    def _pull_callback(self) -> None:
        self._start_pull_timer()
        self._update_buffer()

    def get_buffer(self) -> list[float]:
        if self.pull_on_buffer_read:
            self._update_buffer()
        return self._buffer if self._buffer is not None else []

    def clear_buffer(self, stop_buffering: bool = False) -> list[float]:
        ret = self.get_buffer()
        self._buffer = None if stop_buffering or self._buffer is None else []
        return ret

    def start_buffer(self) -> None:
        if self._buffer is None:
            self._buffer = []

    @abstractmethod
    def _read_from_device(self) -> list[float]:
        pass


class MockBufferInput(BufferInput):
    _init_time: float
    _next_index: int

    def __init__(self, *, buffer: bool = False, pull_rate: int | None = None, pull_on_buffer_read: bool = True, rate: float = 1, mod: int = 50):
        self._init_time = time.time()
        self._next_index = 0
        self.rate = rate
        self.mod = mod
        super().__init__(buffer=buffer, pull_rate=pull_rate, pull_on_buffer_read=pull_on_buffer_read)

    def _read_from_device(self) -> list[float]:
        start_index = self._next_index
        self._next_index = floor((time.time() - self._init_time) * self.rate)
        return [x % self.mod for x in range(start_index, self._next_index)]


class PicoMockBufferInput(BufferInput, USBConnection):
    def __init__(self, *, port: str, buffer: bool = False, pull_rate: int | None = None, pull_on_buffer_read: bool = True):
        BAUD_RATE = 115200
        USBConnection.__init__(
            self,
            port=port,
            baud_rate=BAUD_RATE,
            eol_char='\n'
        )
        BufferInput.__init__(self, buffer=buffer, pull_rate=pull_rate, pull_on_buffer_read=pull_on_buffer_read)

    def _read_from_device(self) -> list[float]:
        lines = self.read_newlines()
        try:
            return [float(str.strip()) for str in lines]
        except ValueError:
            # Bad read from device, throw away data
            print(f'Discarding a corrupted batch of {len(lines)} points')
            return []


def main() -> None:
    pico = MockBufferInput(rate=5, pull_on_buffer_read=True)

    pico.add_input_handler(lambda s: print(f'New input: {s}'))
    while True:
        com = input()
        if com == "r":  # Read buffer
            print(pico.get_buffer())
        elif com == "c":  # Clear buffer
            print(pico.clear_buffer())
        elif com == "s":  # Stop buffering
            print(pico.clear_buffer(True))
        elif com == "b":  # Begin buffering
            pico.start_buffer()
        elif com == "q":  # Quit
            break
    with pico:
        while True:
            com = input()
            if com == "r":  # Read buffer
                print(pico.get_buffer())
            elif com == "c":  # Clear buffer
                print(pico.clear_buffer())
            elif com == "s":  # Stop buffering
                print(pico.clear_buffer(True))
            elif com == "b":  # Begin buffering
                pico.start_buffer()
            elif com == "q":  # Quit
                break
            pico.stop_sampling()


if __name__ == '__main__':
    main()
