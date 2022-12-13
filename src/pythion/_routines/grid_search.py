from __future__ import annotations
from matplotlib.colors import SymLogNorm
from dataclasses import dataclass
from time import sleep
import numpy.typing as npt
import numpy as np
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import logging
from typing import Self, Generator
from contextlib import nullcontext
from io import TextIOWrapper

from pythion._gui.output import Output
from pythion._gui.input import Input
from pythion._routines.measurement_routine import MeasurementRoutine, ValueUpdateSettings
from pythion._routines.file_handling import generate_filename, FileSettings

logger = logging.getLogger('pythion')


# Let's begin with a Heatmap class that will come in handy later.
class Heatmap:
    def __init__(self, settings: GridSearch.HeatmapSettings, labels: list[str], ticks: list[int]):
        self.settings = settings
        self.labels = labels
        self.ticks = ticks
        self.ax = None
        self.cbar_ax = None

    @classmethod
    def from_devices(cls, settings: GridSearch.HeatmapSettings, devices: tuple[GridSearch.Device, GridSearch.Device]):
        labels = [dev.output.label for dev in devices]
        ticks = [dev.values for dev in devices]
        return cls(settings, labels, ticks)

    def plot(self, data: npt.NDArray[np.float64]):
        _, (self.ax, self.cbar_ax) = plt.subplots(1, 2, gridspec_kw={'width_ratios': (0.9, 0.05), 'wspace': 0.2}, figsize=(10, 8))
        self.update(data)
        plt.show(block=False)

    def update(self, data: npt.NDArray[np.float64]):
        if self.ax is None:
            self.plot(data)
            return  # plot calls update on its own, so we can return from here
        assert self.ax is not None, self.cbar_ax is not None
        ylabel, xlabel = self.labels
        yticks, xticks = self.ticks
        self.ax.cla()
        norm = SymLogNorm(self.settings.log_threshold, vmin=self.settings.color_min, vmax=self.settings.color_max)
        palette = sns.color_palette('crest', as_cmap=True)
        sns.heatmap(ax=self.ax, data=data, cmap=palette, cbar_ax=self.cbar_ax, xticklabels=xticks, yticklabels=yticks, norm=norm)
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
    class GridSearchSettings:
        measuring_time: float
        update_graphics: bool
        plot_every: int | None = None  # Setting plot_every to 0 or None will disable live plots.

    @dataclass
    class Device:
        output: Output
        values: list[int]
        wait_time: float

        @classmethod
        def from_stepsize(cls, output: Output, wait_time: float, start_value: int, end_value: int, step_size: int) -> Self:
            values = [round(i) for i in range(start_value, end_value+step_size, step_size)]
            return cls(output, values, wait_time)

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
                 input: Input,
                 settings: GridSearchSettings,
                 plot_settings: HeatmapSettings | None = None,
                 file_settings: FileSettings | None = None
                 ):
        super().__init__()
        self.devices = devices
        self.input = input
        self.settings = settings
        self.file_settings = file_settings
        self.set_output_mode = ValueUpdateSettings.MOVE_KNOBS if settings.update_graphics else ValueUpdateSettings.NO_GRAPHICS

        if len(self.devices) == 2 and plot_settings is not None:  # Initiate heatmap plot (don't show yet!)
            self.heatmap = Heatmap.from_devices(plot_settings, self.devices)
        else:
            self.heatmap = None

        self.add_task(self.execute)

    def execute(self) -> None:
        # Initialize results matrix
        shape = [len(dev.values) for dev in self.devices]
        self.results = np.zeros(shape)

        # Initialize plot
        live_plot = self.heatmap and self.settings.plot_every

        if live_plot:
            # Show plot to prepare live update
            self.run_on_main_thread(self.heatmap.plot, self.results)

        # Initialize outputs
        max_wait = max(dev.wait_time for dev in self.devices)
        for dev in self.devices:
            assert len(dev.values) > 0  # Must be at least one value per Output
            self.set_output(dev.output, dev.values[0], self.set_output_mode, False)
        sleep(max_wait)

        # Start recursive grid search
        self._indices = [0 for _ in self.devices]
        self._counter = 1

        # Configure file writing if required
        filename = generate_filename(self.file_settings) if self.file_settings is not None else None
        with (open(filename, mode='x') if filename is not None else nullcontext()) as file:
            f = None
            if filename is not None:
                f = file
                # Write header row
                f.write(','.join([dev.output.label for dev in self.devices]) + f',{self.input.label}')

            # Measure the very first value manually
            self._measure(f)
            # The rest are measured by recursion
            self._grid_search(0, f)

        # Final plot
        if self.heatmap:
            if live_plot:
                self.run_on_main_thread(self.heatmap.update, self.results)
            else:
                self.run_on_main_thread(self.heatmap.plot, self.results)

    def _grid_search(self, depth: int, file: TextIOWrapper | None) -> bool:
        dev = self.devices[depth]
        is_inverted = self._indices[depth] > 0
        iter_list = list(enumerate(dev.values))
        first = True
        for i, val in reversed(iter_list) if is_inverted else iter_list:
            if self.handler._cancelled:
                return False
            if not first:
                self._indices[depth] = i
                logger.debug('GridSearch:     setting value')
                self.set_output(dev.output, val, self.set_output_mode, False)
                sleep(dev.wait_time)
                self._measure(file)
            else:
                first = False
            if depth+1 < len(self.devices):
                if not self._grid_search(depth + 1, file):
                    return False
        return True
        # Return True to its caller if run to completion. Return False (early) if
        # cancel flag is set to true, or child routine discover cancel flag set to true

    def _measure(self, file: TextIOWrapper | None) -> None:
        value = self.measure(self.input, self.settings.measuring_time)
        self.results[tuple(self._indices)] = value
        if self.heatmap and self.settings.plot_every:
            if self._counter % self.settings.plot_every == 0:
                self.run_on_main_thread(self.heatmap.update, self.results)
            self._counter = self._counter + 1
        if file is not None:
            assert isinstance(file, TextIOWrapper)
            device_settings_string = ','.join(str(val) for val in self._get_set_values())
            file.write(f'\n{device_settings_string},{value}')

    def _get_set_values(self) -> Generator[float, None, None]:
        yield from (device.values[current_index] for device, current_index in zip(self.devices, self._indices))


def read_file(filepath: str, plot_settings: GridSearch.HeatmapSettings | None = None) -> Self:
    # To avoid allocating all data in memory, file is read in two passes:
    # First determining the step sizes, and second, getting the values.

    with open(filepath, 'rt') as file:
        header = file.readline()
        device_names = header.split(',')
        _ = device_names.pop()  # Todo: add title to plot
        device_values = [set() for _ in device_names]
        for line in file.readlines():
            vals = line.split(',')[0:-1]
            for val, dev_vals in zip(vals, device_values):
                dev_vals.add(int(val))
        dims, sorted_device_values = zip(*[(len(dev_vals), sorted(dev_vals)) for dev_vals in device_values])
        results = np.empty(dims)
        results[:] = 0
        file.seek(0)  # Set read pointer at beginning again
        file.readline()
        for line in file.readlines():
            vals = line.split(',')
            measurement_val = vals.pop()
            indices = tuple(dev_vals.index(int(val)) for dev_vals, val in zip(sorted_device_values, vals))
            results[indices] = measurement_val

    if len(dims) == 2:
        if plot_settings is None:
            plot_settings = GridSearch.HeatmapSettings(0, 3000, 1)
        # Flip y axis so that 0 is in bottom left corner
        sorted_device_values[0].reverse()
        results = np.flipud(results)
        heatmap = Heatmap(plot_settings, device_names, sorted_device_values)
        heatmap.update(results)
    return results


if __name__ == '__main__':
    filename = 'gridresults/221208T1425_results.csv'
    print(read_file(filename))
    input('Press enter to continue')
