import matplotlib
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


class PlotBase(FigureCanvasQTAgg):
    def __init__(self, parent: QWidget):
        fig = Figure(figsize=(1, 1))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot(self, x: list[float], y: list[float]) -> None:
        self.axes.plot(x, y)
