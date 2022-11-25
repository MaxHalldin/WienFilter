from pythion import Output, GUIUpdater, HeatMap
from typing import Callable
from time import sleep
import numpy as np


def grid_search(*args: tuple[Output, list[int], float],
                measure: Callable[[], float],
                result_plot: HeatMap | None = None):
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
    obj = GridSearcher(args, measure, result_plot)
    obj.initialize()
    obj.grid_search()


class GridSearcher:
    def __init__(self,
                 devices: tuple[tuple[Output, list[int], float], ...],
                 measure: Callable[[], float],
                 result_plot: HeatMap | None):
        self.devices = devices
        shape = [len(values) for _, values, _ in devices]
        self.results = np.empty(shape)
        self.measure = measure
        self.result_plot = result_plot

    def initialize(self) -> None:
        max_wait = 0.
        for output, values, wait_time in self.devices:
            assert len(values) > 0  # Must be at least one value per Output
            max_wait = max(max_wait, wait_time)
            print(output, values[0])
            GUIUpdater.update(output, "set_value", values[0], True)
        self.indices = [0 for _ in self.devices]
        print(f'Setting position {self.indices}')
        print(f'Sleeping for {max_wait} s')
        sleep(max_wait)

    def grid_search(self) -> None:
        try:
            self._measure()
            self._grid_search(0)
            del self.indices
            if self.result_plot:
                assert len(self.devices) == 2  # Can only heatmap-plot 2D grid searches!
                labels, ticks = zip(*[(device.namestr, values) for device, values, _ in reversed(self.devices)])
                print(labels, ticks)
                GUIUpdater.update(self.result_plot, 'plot', self.results, *labels, *ticks)
        except AttributeError:
            raise Exception('Must call initialize before grid_search!')

    def _grid_search(self, depth: int) -> None:
        """
        This is a local and recursice implementation of the grid search algorithm.
        When _grid_search is called, a grid search with measurements is conducted on all devices listed in 'args'.
        They will be optimally iterated assuming configuration as specified by the indices list
        All devices are assumed to already be configured in the position corresponding to the first sample point in the
        grid search. Starting with '_initialize' and following up with recursive use of _grid_search guarantees that this
        is the case.
        This way, only one device setting will change inbetween each call. Therefore, every change of device setting is
        followed by waiting the designated settling time, then taking a measurement.

        Additionally, a np array is passed to each call in order to store the results. A shared list of indices is passed
        around between the function calls, both as an argument and as a return value, to be used for correctly indexing the
        results nd-matrix.

        args here follow the same pattern as in the entry method above, but devices are recursively "stripped"
        from the list as we go deeper down the call stack. However, this method will never be called with args being empty.

        Note that this implementation does NOT perform a measurement in the initial configuration!! Therefore, the entry function
        will perform a single measurement after initialization is complete.
        """
        output, values, wait_time = self.devices[depth]
        is_inverted = self.indices[depth] > 0
        iter_list = list(enumerate(values))
        first = True
        for i, val in reversed(iter_list) if is_inverted else iter_list:
            if not first:
                self.indices[depth] = i
                GUIUpdater.update(output, "set_value", val, True)
                print(f'Position {self.indices} set')
                print(f'Sleeping for {wait_time} s')
                sleep(wait_time)
                self._measure()
            else:
                first = False
            if depth+1 < len(self.devices):
                self._grid_search(depth + 1)

    def _measure(self) -> None:
        print(f'Measuring for position {self.indices}\n')
        self.results[tuple(self.indices)] = self.measure()
