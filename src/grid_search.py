from pythion import Output, GUIUpdater
from time import sleep


def grid_search(*args: tuple[Output, list[int], float]) -> None:
    """
    This is an example of a worker function, that defines something tedious that should be done over
    some period of time. Such a function has to be run using an Action component. Also, any updates to the
    GUI from this function must be handled via the GUIUpdater.update method, see below.

    This particular function conducts a grid search over some Output devices. For every device to include in the
    grid search, pass a tuple to the function as an argument. Every such tuple should be of the form:
        (OutputObj, ValuesToCheck, WaitTime)
    where:
        OutputObj is a reference to the Output component instance,
        ValuesToCheck is a (preferrably ordered) list of output values to check with this output, and
        WaitTime is the minimum time (in seconds) of waiting that is required for the output device to "settle"
            after changing the value, before measuring or similar.

    The internal variable 'inverted' is used to keep track of whether the outputs were last set to the first value
        in their value list (inverted[i] = False) or the last value in their value list (inverted[i] = True). This
        allows iterating over the values in either forward- or backwards direction, eliminating the need for "jumps"
        back to the initial value.
    """
    inverted = [False for _ in args]
    _initialize(*args, min_wait_time=0)
    _grid_search(*args, inverted=inverted)


def _grid_search(*args: tuple[Output, list[int], float], inverted: list[bool]) -> list[bool]:
    """
    This is a local and recursice implementation of the grid search algorithm.
    It will only be called with at least one device in args. Thanks to the inversion
    optimization, all other devices can always be assumed to be in the right position.
    Whenever an Output changes its value, it waits the given time and then initializes
    a measurement. Additionally, the last output in the call chain will activate one measurement
    the first time it is called.
    """
    output, values, wait_time = args[0]
    first = True
    res = inverted[1:]
    for val in (reversed(values) if inverted[0] else values):
        if not first:
            GUIUpdater.update(output, "set_value", val, True)
            print(f'Sleeping {wait_time}')
            sleep(wait_time)
            print('Measured')
        else:
            if len(args) == 1:
                print('Measured')
            first = False
        if len(args) > 1:
            res = _grid_search(*args[1:], inverted=res)

    inverted = [not inverted[0], *res]
    return inverted


def _initialize(*args: tuple[Output, list[int], float], min_wait_time: float) -> list[bool]:
    if not args:
        sleep(min_wait_time)
    else:
        output, values, wait_time = args[0]
        assert values  # Must be at least one value per Output
        GUIUpdater.update(output, "set_value", values[0], True)
        _initialize(*args[1:], min_wait_time=max(min_wait_time, wait_time))
