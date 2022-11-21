import matplotlib  # type: ignore
from time import time

from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # type: ignore
from matplotlib.figure import Figure  # type: ignore
from pythion.connections import InputInterface

matplotlib.use('Qt5Agg')


class PlotBase(FigureCanvasQTAgg):  # type: ignore
    def __init__(self, *, parent: QWidget):
        fig = Figure(figsize=(1, 1))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot(self, x: list[float], y: list[float]) -> None:
        self.axes.cla()
        self.axes.plot(x, y)
        self.draw()
        print('Plotted!')


class PlotStream(PlotBase):
    init_time: float  # Standard time
    time_list: list[float]  # Time relative to init_time
    data_list: list[float]
    timespan: int

    def __init__(self, *, parent: QWidget, input: InputInterface, timespan: int = 60):
        super().__init__(parent=parent)
        self.init_time = time()
        self.time_list = []
        self.data_list = []
        self.timespan = timespan
        self.axes.set_xlim([0, 60])
        self.axes.set_ylim([0, 100])
        input.add_input_handler(self._add_point)

    def _add_point(self, data: float) -> None:
        current_time = time()
        cut_time = current_time - self.timespan - self.init_time
        cut_index = len(self.time_list)
        for i, t in enumerate(self.time_list):
            if t > cut_time:
                cut_index = i
                break
        self.time_list = self.time_list[cut_index:]
        self.data_list = self.data_list[cut_index:]
        self.time_list.append(current_time-self.init_time)
        self.data_list.append(data)
        self._update()

    def _update(self) -> None:
        self.plot(self.time_list, self.data_list)
