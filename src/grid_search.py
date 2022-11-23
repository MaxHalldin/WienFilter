from pythion import Output, GUIUpdater
from time import sleep


def grid_search(*args: tuple[Output, list[int], float]) -> None:
    """
    Every argument is a tuple of the type (OutputObj, ValuesToCheck, WaitTime)
    """
    print(args)
    _grid_search(*args, min_wait_time=0)


def _grid_search(*args: tuple[Output, list[int], float], min_wait_time: float) -> None:
    if not args:
        # Time to measure!
        sleep(min_wait_time)
        print('Measured!')
    else:
        output, values, wait_time = args[0]
        print(f'Looping over {output.name}')
        for val in values:
            print(f'Setting {output.name} to {val}')
            GUIUpdater.update(output, "set_value", val, True)
            _grid_search(*args[1:], min_wait_time=max(min_wait_time, wait_time))
            min_wait_time = 0
