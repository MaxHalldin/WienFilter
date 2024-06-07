from abc import ABC, abstractmethod
from typing import Callable, Self, Any
from threading import Timer
import logging

logger = logging.getLogger('pythion')


class InputInterface(ABC):
    """
    Abstract base class for an input device. A derived class is to be made for every type of output,
    and the connection details should be covered in the enter/exit methods.
    Both Push and Pull data flow is supported. For push,
    you provide a sampling rate (Hz) at which current will be measured.
    Then, add listeners with the addInputHandlers method.
    To use Pull, you simple query a value using the read method.

    To implement the class, define a subclass which defines
    """
    _input_handlers: list[Callable[[float], None]]

    def __init__(self) -> None:
        self._input_handlers = []

    def add_input_handler(self, onValueChanged: Callable[[float], None]) -> None:
        self._input_handlers.append(onValueChanged)

    @abstractmethod
    def start_sampling(self, sample_rate: int) -> None:
        pass

    @abstractmethod
    def stop_sampling(self) -> None:
        pass

    def _invoke_handlers(self, value: float) -> None:
        for handler in self._input_handlers:
            handler(value)

    @abstractmethod
    def read(self) -> float:
        pass

    # __enter__ and __exit__ are defined since most Inputs require IO handling, and it's
    # nice if all Inputs then accept the use of context managers. However, to avoid masking
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


class TimerInput(InputInterface):
    """
    An abstract subclass of Input that also provides a handy timer four
    sampling asynchronously at a constant rate. The _read method can be
    overloaded to do whatever needs to be done periodically, while the
    read method handles external calls for a single value. In this default
    setting, they do the same thing.
    """
    _timer: Timer | None
    _wait_time: float
    _in_context_manager: bool

    def __init__(self) -> None:
        self._timer = None
        self._in_context_manager = False
        super().__init__()

    def __enter__(self) -> Self:
        super().__enter__()
        self._in_context_manager = True
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop_sampling()
        self._in_context_manager = False
        super().__exit__()

    @abstractmethod
    def _read(self) -> float:
        pass

    def read(self) -> float:
        return self._read()

    def start_sampling(self, sample_rate: int) -> None:
        if not self._in_context_manager:
            logger.warning('TimerInput:     Attempted to start a timer without context manager!')
        else:
            self._wait_time = 1 / sample_rate
            self._start_sampling()

    def _start_sampling(self) -> None:
        self._timer = Timer(self._wait_time, self._callback)
        self._timer.start()

    def stop_sampling(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _callback(self) -> None:
        self._start_sampling()
        self._invoke_handlers(self._read())


class MockInput(TimerInput):
    _val: float = 0

    def _read(self) -> float:
        self._val = (self._val + 1) % 10
        return self._val

from srcMAX.pythionMAX._connectionsMAX.input_interfaceMAX import TimerInput
import random as rd
class MockCAEN(TimerInput):
    _val: float = 10
    
    def _read_from_device(self) -> list[float] | None:
        return ['OK']*4

    def _write(self, cmd: str, par: str, val: int|str|None = None, ch: int|None = None, bd = 0) -> None:
        msg = f"{bd} {cmd} {ch} {par} {val}"
        logger.debug(f"MockCAEN:        message: {msg}.")
        #print(msg)

 
    def _read(self) -> None:
        self._val = self._val + (rd.random()-0.5)*2
        return self._val

def main() -> None:
    x = MockInput()
    x.add_input_handler(print)
    x.start_sampling(3)
    input('Press enter to quit reading\n')
    x.stop_sampling()
    input('Enter to exit')

if __name__ == '__main__':
    main()
