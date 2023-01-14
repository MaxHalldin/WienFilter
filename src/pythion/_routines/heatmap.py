from __future__ import annotations
from dataclasses import dataclass
from matplotlib.colors import SymLogNorm, Normalize
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import numpy.typing as npt


class Heatmap:
    @dataclass
    class Settings:
        color_min: float
        color_max: float
        log_threshold: float | None
        max_label_count: int

    def __init__(self, settings: Heatmap.Settings, labels: list[str], ticks: tuple[list[int], list[int]], cbar_label: str, palette=None):
        self.settings = settings
        self.labels = labels
        self.yticks = self.filter_ticklabels(ticks[0], settings.max_label_count)
        self.xticks = self.filter_ticklabels(ticks[1], settings.max_label_count)
        self.palette = palette if palette is not None else sns.color_palette('crest', as_cmap=True)
        self.ax = None
        self.fig = None
        self.cbar_ax = None
        self.cbar_label = cbar_label

    def plot(self, data: npt.NDArray[np.float64]):
        self.fig, (self.ax, self.cbar_ax) = plt.subplots(1, 2, gridspec_kw={'width_ratios': (0.9, 0.05), 'wspace': 0.2}, figsize=(10, 8))
        self.update(data)
        plt.show(block=False)

    @staticmethod
    def filter_ticklabels(labels: list[int], max_labels: int):
        labels = [str(i) for i in labels]
        while len([s for s in labels if s != '']) > max_labels:
            # Iteratively set every other label to '' until number of remaining labels are equal or lower than max:labels
            remove_next = True
            for i, s in enumerate(labels):
                if s == '':
                    continue
                remove_next = not remove_next
                if remove_next:
                    labels[i] = ''
        return labels

    def update(self, data: npt.NDArray[np.float64]):
        if self.ax is None:
            self.plot(data)
            return  # plot calls update on its own, so we can return from here
        assert self.ax is not None, self.cbar_ax is not None
        ylabel, xlabel = self.labels
        self.ax.cla()
        if self.settings.log_threshold is not None:
            if self.settings.log_threshold == 0:
                self.settings.log_threshold = self.settings.color_min
            norm = SymLogNorm(self.settings.log_threshold, vmin=self.settings.color_min, vmax=self.settings.color_max)
        else:
            norm = Normalize(self.settings.color_min, self.settings.color_max, clip=True)
        sns.heatmap(ax=self.ax, data=data, cmap=self.palette, cbar_ax=self.cbar_ax, xticklabels=self.xticks, yticklabels=self.yticks, norm=norm,
                    cbar_kws={'label': self.cbar_label})
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        plt.draw()
