from __future__ import annotations
from dataclasses import dataclass
from matplotlib.colors import SymLogNorm
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import numpy.typing as npt


class Heatmap:
    @dataclass
    class Settings:
        color_min: float
        color_max: float
        log_threshold: float

    def __init__(self, settings: Heatmap.Settings, labels: list[str], ticks: list[int]):
        self.settings = settings
        self.labels = labels
        self.ticks = ticks
        self.ax = None
        self.cbar_ax = None

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
