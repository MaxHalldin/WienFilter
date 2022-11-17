from abc import ABC, abstractmethod
from typing import Callable, Self, Any
from threading import Timer


class Input(ABC):
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
    def end_sampling(self) -> None:
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


class MockInput(Input):
    _timer: Timer | None
    _wait_time: float

    def __init__(self) -> None:
        self._timer = None
        super().__init__()

    def read(self) -> float:
        return 0

    def start_sampling(self, sample_rate: int) -> None:
        self._wait_time = 1 / sample_rate
        self._start_sampling()

    def _start_sampling(self) -> None:
        self._timer = Timer(self._wait_time, self._callback)
        self._timer.start()

    def end_sampling(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _callback(self) -> None:
        self._start_sampling()
        self._invoke_handlers(self.read())


def main() -> None:
    x = MockInput()
    x.add_input_handler(print)
    x.start_sampling(3)
    input('Press enter to quit reading\n')
    x.end_sampling()
    input('Enter to exit')


if __name__ == '__main__':
    main()
