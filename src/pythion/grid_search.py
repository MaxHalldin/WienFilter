from PyQt5.QtCore import pyqtSlot
from pythion import Output, GUIUpdater, Action
from dataclasses import dataclass
from pythion.connections import BufferInput
from time import sleep
import numpy.typing as npt
import numpy as np
from statistics import mean
from PyQt5.QtWidgets import QWidget
import seaborn as sns
import matplotlib.pyplot as plt


@dataclass
class OutputConfiguration:
    output: Output
    values: list[int]
    wait_time: float


class GridSearch(Action):
    """
    This class is an extension of the Action GUI class, meaning that it effectively has a start button and is able to run asynchronously.
    """
    devices: list[OutputConfiguration]
    measure_time: float
    input: BufferInput
    results: npt.NDArray | None
    move_knobs: bool
    # Plotting parameters
    ax: plt.Axes | None
    cbar_ax: plt.Axes | None = None
    labels: tuple[str, str] | None
    ticks: tuple[list[int], list[int]] | None
    plot_every: int
    current: int

    def __init__(self, *, input: BufferInput, measuring_time: float, parent: QWidget, move_knobs: bool = True, plot_every: int = 1):
        self.input = input
        self.measure_time = measuring_time
        self.results = None
        self.move_knobs = move_knobs
        self.devices = []
        self.ax = None
        self.cbar_ax = None
        self.labels = None
        self.ticks = None
        self.plot_every = plot_every
        self.current = 0

        super().__init__(action=self.run, args=[], kwargs={}, parent=parent, text='Start Grid Search')

    def add_device(self, output_control: Output, values: list[int], wait_time: float) -> None:
        self.devices.append(OutputConfiguration(output_control, values, wait_time))

    def write_to_file(self, filepath):
        raise NotImplementedError('Not able to write to file yet!')

    def before_execution(self):
        shape = [len(d.values) for d in self.devices]
        self.results = np.zeros(shape)
        if len(self.devices) == 2:
            grid_kws = {'width_ratios': (0.9, 0.05), 'wspace': 0.2}
            _, (self.ax, self.cbar_ax) = plt.subplots(1, 2, gridspec_kw=grid_kws, figsize=(10, 8))
            plt.show()
            self.labels, self.ticks = zip(*[(d.output.namestr, d.values) for d in self.devices])
            self._update_plot()

    def _update_plot(self):
        ylabel, xlabel = self.labels
        yticks, xticks = self.ticks
        sns.heatmap(ax=self.ax, data=self.results, cmap="crest", cbar_ax=self.cbar_ax, xticklabels=xticks, yticklabels=yticks)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        plt.draw()

    def run(self):
        AsyncWorker(self)

    @pyqtSlot(list, float)
    def measure(self, indices: list[int], value: float):
        self.results[tuple(indices)] = value
        if self.ax is not None and (self.current % self.plot_every == 0):
            self._update_plot()
        self.current = self.current + 1

    @pyqtSlot()
    def complete(self):
        self.current = 0


class AsyncWorker:
    devices: list[OutputConfiguration]
    input: BufferInput
    measure_time: float
    move_knobs: bool
    indices: list[int] | None
    parent: GridSearch

    def __init__(self, parent: GridSearch) -> None:
        self.parent = parent
        self.devices = parent.devices
        self.input = parent.input
        self.move_knobs = parent.move_knobs
        self.measure_time = parent.measure_time
        self.indices = [0 for _ in self.devices]

        self.input.start_buffer()
        self.initialize_outputs()
        self.measure()
        self._grid_search(0)
        self.input.clear_buffer(True)
        GUIUpdater.update(parent, "complete")

    def measure(self) -> None:
        self.input.clear_buffer()
        # Wait for self.measure_time as many times as needed to recieve at least one measurement
        vals = []
        while True:
            sleep(self.measure_time)
            vals = self.input.clear_buffer()
            if vals:
                break
        GUIUpdater.update(self.parent, "measure", self.indices, float(mean(vals)))

    def initialize_outputs(self) -> None:
        max_wait = 0.
        for d in self.devices:
            assert len(d.values) > 0  # Must be at least one value per Output
            max_wait = max(max_wait, d.wait_time)
            GUIUpdater.update(d.output, "set_value", d.values[0], self.move_knobs)
        sleep(max_wait)

    def _grid_search(self, depth: int) -> None:
        d = self.devices[depth]
        is_inverted = self.indices[depth] > 0
        iter_list = list(enumerate(d.values))
        first = True
        for i, val in reversed(iter_list) if is_inverted else iter_list:
            if not first:
                self.indices[depth] = i
                GUIUpdater.update(d.output, "set_value", val, self.move_knobs)
                sleep(d.wait_time)
                self.measure()
            else:
                first = False
            if depth+1 < len(self.devices):
                self._grid_search(depth + 1)

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
