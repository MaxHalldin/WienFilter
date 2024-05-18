import matplotlib  # type: ignore
import numpy as np
import numpy.typing as npt
from time import time

from PyQt5.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from matplotlib.lines import Line2D  # type: ignore
from srcMAX.pythionMAX._connectionsMAX.input_interfaceMAX import InputInterface
from srcMAX.pythionMAX._layoutMAX.ui_plotframeMAX import Ui_PlotFrame

matplotlib.use('Qt5Agg')


class PlotFrame(QWidget, Ui_PlotFrame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class PlotBase(FigureCanvasQTAgg):  # type: ignore
    def __init__(self, *, parent: QWidget):
        self.sizeHint = (100, 100)
        self.plt = Figure(figsize=(1, 1))
        self.axes = self.plt.add_subplot(111)
        super().__init__(self.plt)
        self.figure.subplots_adjust(left=0.2)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.frame = PlotFrame()
        self.frame.mainLayout.addWidget(self)


class LinePlot(PlotBase):
    _line: Line2D
    _xlim_set: bool
    _ylim_set: bool

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)
        self._xlim_set = False
        self._ylim_set = False
        self._line = None

    def set_xlim(self, xlim: tuple[float, float]) -> None:
        self._xlim_set = True
        self.axes.set_xlim(xlim)

    def set_ylim(self, ylim: tuple[float, float]) -> None:
        self._ylim_set = True
        self.axes.set_ylim(ylim)

    def _update_plot(self, x: npt.ArrayLike, y: npt.ArrayLike) -> None:
        if self._line is None:
            self._line, = self.axes.plot(x, y)
        else:
            self._line.set_ydata(y)
            self._line.set_xdata(x)
            if not (self._xlim_set and self._ylim_set):
                self.axes.relim()
                self.axes.autoscale_view()
        self.draw()


class PlotStream(LinePlot):
    init_time: float | None  # Standard time
    time_list: npt.NDArray[np.float64]  # Time relative to init_time
    data_list: npt.NDArray[np.float64]
    timespan: int
    fix_scale: bool  # If set to true, then x values will be fixed between 0 and timespan.
    _cutting: bool  # Internal state variable that keeps track of whether data has overflown the timespan

    def __init__(self, *, parent: QWidget | None = None, input: InputInterface, timespan: int = 60, fix_scale: bool = False):
        super().__init__(parent=parent)
        self.init_time = None
        self.time_list = np.empty((0,))
        self.data_list = np.empty((0,))
        self.timespan = timespan
        self.fix_scale = fix_scale
        self._cutting = False
        self.set_xlim((0, timespan))
        input.add_input_handler(self._add_point)

    def _add_point(self, data: float) -> None:
        current_time = time()
        if self.init_time is None:
            self.init_time = current_time
        cut_time = current_time - self.timespan - self.init_time
        cut_index = np.searchsorted(self.time_list, cut_time)
        cut = cut_index != 0
        if cut:
            cut_index = cut_index - 1  # Keep one data point to the left of the cut.
            self._cutting = True
        self.time_list = np.append(self.time_list[int(cut_index):], current_time-self.init_time)
        self.data_list = np.append(self.data_list[int(cut_index):], data)

        plot_time = self.time_list
        if self._cutting:
            if self.fix_scale:
                plot_time = self.time_list - self.time_list[-1] + self.timespan
            else:
                self.set_xlim(((self.time_list[-1]-self.timespan), self.time_list[-1]))
        if len(plot_time) != len(self.data_list):
            raise Exception('Sampling too fast!')
        self._update_plot(plot_time, self.data_list)
