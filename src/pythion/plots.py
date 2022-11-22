import matplotlib  # type: ignore
import numpy as np
from numpy.typing import ArrayLike
from time import time

from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from matplotlib.lines import Line2D  # type: ignore
from pythion.connections import InputInterface

matplotlib.use('Qt5Agg')


class PlotBase(FigureCanvasQTAgg):  # type: ignore
    def __init__(self, *, parent: QWidget):
        fig = Figure(figsize=(1, 1))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def set_axes(self, xlim: tuple[float, float] | None = None, ylim: tuple[float, float] | None = None) -> None:
        if xlim is not None:
            self.axes.set_xlim(xlim)
        if ylim is not None:
            self.axes.set_ylim(ylim)


class LinePlot(PlotBase):
    _line: Line2D
    _xlim_set: bool
    _ylim_set: bool

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)
        self._line = None

    def set_xlim(self, xlim: tuple[float, float]) -> None:
        self._xlim_set = True
        self.axes.set_xlim(xlim)

    def set_ylim(self, ylim: tuple[float, float]) -> None:
        self._ylim_set = True
        self.axes.set_ylim(ylim)

    def _update_plot(self, x: ArrayLike, y: ArrayLike) -> None:
        if self._line is None:
            self._line, = self.axes.plot(x, y)
        else:
            self._line.set_ydata(y)
            self._line.set_xdata(x)
            if not (self._xlim_set and self._ylim_set):
                print('Hej')
                self.axes.relim()
                self.axes.autoscale_view()
        self.draw()


class PlotStream(LinePlot):
    init_time: float  # Standard time
    time_list: ArrayLike  # Time relative to init_time
    data_list: ArrayLike
    timespan: int
    fix_scale: bool  # If set to true, then x values will be fixed between 0 and timespan.
    _cutting: bool  # Internal state variable that keeps track of whether data has overflown the timespan

    def __init__(self, *, parent: QWidget, input: InputInterface, timespan: int = 60, fix_scale: bool = False):
        super().__init__(parent=parent)
        self.init_time = time()
        self.time_list = np.empty((0,))
        self.data_list = np.empty((0,))
        self.timespan = timespan
        self.fix_scale = fix_scale
        self._cutting = False
        self.set_xlim((0, timespan))
        input.add_input_handler(self._add_point)

    def _add_point(self, data: float) -> None:
        current_time = time()
        cut_time = current_time - self.timespan - self.init_time
        cut_index = np.searchsorted(self.time_list, cut_time)
        cut = cut_index != 0
        if cut:
            cut_index = cut_index - 1  # Keep one data point to the left of the cut.
            self._cutting = True
        self.time_list = np.append(self.time_list[cut_index:], current_time-self.init_time)
        self.data_list = np.append(self.data_list[cut_index:], data)

        plot_time = self.time_list
        if self._cutting:
            if self.fix_scale:
                plot_time = self.time_list - self.time_list[-1] + self.timespan  # type: ignore
            else:
                self.set_xlim(((self.time_list[-1]-self.timespan), self.time_list[-1]))  # type: ignore
        if len(plot_time) != len(self.data_list):
            raise Exception('Sampling too fast!')
        self._update_plot(plot_time, self.data_list)
