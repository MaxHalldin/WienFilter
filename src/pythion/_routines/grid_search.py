from __future__ import annotations
from PyQt5.QtCore import pyqtSlot
from matplotlib.colors import SymLogNorm
from dataclasses import dataclass
from pythion._connections.buffer_input import BufferInput
from time import sleep
import numpy.typing as npt
import numpy as np
from statistics import mean
from PyQt5.QtWidgets import QWidget
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from datetime import datetime
from itertools import product
from typing import Self, Generator
import logging

from pythion._gui.output import Output
from pythion._gui.input import Input
from pythion._routines.measurement_routine import MeasurementRoutine, ValueUpdateSettings

logger = logging.getLogger('pythion')


# Let's begin with a Heatmap class that will come in handy later.
class Heatmap:
    def __init__(self, settings: GridSearch.HeatmapSettings, devices: tuple[GridSearch.Device, GridSearch.Device]):
        self.settings = settings
        self.labels = [dev.name for dev in devices]
        self.ticks = [dev.values for dev in devices]

    def plot(self, data: npt.NDArray[np.float64]):
        _, (self.ax, self.cbar_ax) = plt.subplots(1, 2, gridspec_kw={'width_ratios': (0.9, 0.05), 'wspace': 0.2}, figsize=(10, 8))
        self.update(data)
        plt.show(block=False)

    def update(self, data: npt.NDArray[np.float64]):
        ylabel, xlabel = self.labels
        yticks, xticks = self.ticks
        self.ax.cla()
        norm = SymLogNorm(self.settings.log_threshold, vmin=self.settings.color_min, vmax=self.settings.color_max)
        palette = sns.color_palette('crest', as_cmap=True)
        sns.heatmap(ax=self.ax, data=self.results, cmap=palette, cbar_ax=self.cbar_ax, xticklabels=xticks, yticklabels=yticks, norm=norm)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        plt.draw()


class GridSearch(MeasurementRoutine):
    # Now, three small but helpful dataclasses
    @dataclass
    class HeatmapSettings:
        color_min: float
        color_max: float
        log_threshold: float

    @dataclass
    class FileSettings:
        filepath: str = './',
        filename: str = 'grid_results',
        add_datetime: bool = True

    @dataclass
    class Device:
        output: Output
        values: list[int]
        wait_time: float

    @dataclass
    class GridSearchSettings:
        measuring_time: float
        update_graphics: bool
        plot_every: int | None = None

    devices: tuple[Device, ...]
    input: Input
    settings: GridSearchSettings
    results: npt.NDArray[np.float64]
    heatmap: Heatmap | None
    file_settings: FileSettings | None

    _indices: list[int]
    _counter: int

    def __init__(self,
                 *devices: Device,
                 input: BufferInput,
                 settings: GridSearchSettings,
                 plot_settings: HeatmapSettings | None,
                 file_settings: FileSettings | None
                 ):
        super().__init__()
        self.devices = devices
        self.input = input
        self.settings = settings
        self.file_settings = file_settings
        self.set_output_mode = ValueUpdateSettings.MOVE_KNOBS if settings.update_graphics else ValueUpdateSettings.NO_GRAPHICS

        shape = [len(vals) for vals in self.values]
        self.results = np.zeros(shape)

        if len(self.devices) == 2 and plot_settings is not None:  # Plot a heatmap
            self.heatmap = Heatmap(plot_settings, self.devices)
        else:
            self.heatmap = None

        self.add_task(self.execute)

    def execute(self) -> None:
        # Initialize plot
        live_plot = self.heatmap and not self.plot_every == 0
        if live_plot:
            # Show plot to prepare live update
            self.run_on_main_thread(self.heatmap.plot, self.results, self.devices)

        # Initialize outputs
        max_wait = max(dev.wait_time for dev in self.devices)
        for dev in self.devices:
            assert len(dev.values) > 0  # Must be at least one value per Output
            self.set_output(dev.output, dev.values[0], self.set_output_mode, False)
        sleep(max_wait)

        # Start recursive grid search
        self._indices = [0 for _ in self.devices]
        self._counter = 1
        # Measure the very first value manually
        self._measure()
        # The rest are measured by recursion
        self._grid_search(0)
        self.input.clear_buffer(True)

    def _grid_search(self, depth: int) -> bool:
        dev = self.devices[depth]
        is_inverted = self._indices[depth] > 0
        iter_list = list(enumerate(dev.values))
        first = True
        for i, val in reversed(iter_list) if is_inverted else iter_list:
            if self.context._cancelled:
                return False
            if not first:
                self._indices[depth] = i
                logger.debug('GridSearch:     setting value')
                self.set_output(dev.output, val, self.set_output_mode, False)
                sleep(dev.wait_time)
                self._measure()
            else:
                first = False
            if depth+1 < len(self.devices):
                if not self._grid_search(depth + 1):
                    return False
        return True
        # Return True to its caller if run to completion. Return False (early) if
        # cancel flag is set to true, or child routine discover cancel flag set to true

    def _measure(self) -> None:
        value = self.measure(self.input, self.settings.measuring_time)
        self.results[tuple(self._indices)] = value
        if self.heatmap:
            if self._counter % self.plot_every != 0:
                self.run_on_main_thread(self.heatmap.update, self.results)
            self.counter = self.counter + 1
        if self.file_settings:
            pass  # Write to file here

        self.results.update_plot()

    # def write_to_file(settings: GridSearch.FileSettings, data: ) -> None:
        # f = filepath
        # if add_datetime:
            # now = datetime.now()
            # f = f + f'{now:%y%m%d}T{now:%H%M}_'
        # f = f + filename + '.csv'

        # nonempty_names = [name if name else 'Unnamed Output' for name in self.names]
        # header = ','.join(nonempty_names + [self.measurement_str])
        # with open(f, 'wt') as file:
            # file.write(header)
            # for config in self._iterate_matrix():
                # indices, values = zip(*config)
                # measurement = self.value_at(tuple(indices))
                # file.write(f"\n{ ','.join([str(x) for x in values]) },{measurement}")
        # logger.info('GridSearch:     Finished writing to file!')

    # @classmethod
    # def from_file(cls, filepath: str) -> Self:
        # # To avoid allocating all data in memory, file is read in two passes:
        # # First determining the step sizes, and second, getting the values.
        # device_values: list[set[int]]
        # dims: tuple[int, ...]
        # vals: list[str]

        # with open(filepath, 'rt') as file:
            # header = file.readline()
            # device_names = header.split(',')
            # measurement_name = device_names.pop()
            # device_values = [set() for _ in device_names]
            # for line in file.readlines():
                # vals = line.split(',')[0:-1]
                # for val, dev_vals in zip(vals, device_values):
                    # dev_vals.add(int(val))
            # dims, sorted_device_values = zip(*[(len(dev_vals), sorted(dev_vals)) for dev_vals in device_values])
            # results = np.empty(dims)
            # results[:] = 0
            # file.seek(0)  # Set read pointer at beginning again
            # file.readline()
            # for line in file.readlines():
                # vals = line.split(',')
                # measurement_val = vals.pop()
                # indices = tuple(dev_vals.index(int(val)) for dev_vals, val in zip(sorted_device_values, vals))
                # results[indices] = measurement_val
            # res = cls(*zip(sorted_device_values, device_names), measurement_str=measurement_name, show_plot=False)
            # res.set_final_results(results)
            # print(results)
            # res.update_plot()
            # return res


#if __name__ == '__main__':
    #GridSearchResults.from_file('221130T1200_grid_results.csv')
    #plt.show()
