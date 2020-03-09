from .core import BaseHist

from typing import Tuple, Optional, Callable

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


class Hist(BaseHist):
    def _validate_axes(self):
        pass

    def pull_plot(
        self,
        callback: Callable,
        height_ratios: Tuple[float, float] = (1, 0.2),
        color: str = "#444444",
        ecolor: str = "#ff0000",
        title: Optional[str] = None,
        ylabel: str = "Counts",
        figsize: Tuple[float, float] = (8, 8),
        grid: bool = True,
        n_ticks: Optional[float] = None,
        n_ticks_pull: Optional[float] = None,
        sigma: Optional[float] = None,
        ax: Optional[mpl.axes.Axes] = None,
        pull_ax: Optional[mpl.axes.Axes] = None,
    ) -> Tuple[mpl.axes.Axes, mpl.axes.Axes]:
        """
        :param callback:
            Callable used for the pull plot.
        :param height_ratios:
            Height ratio between the main plot and the pull plot.
        :param color:
            Color of bars and lines.
        :param ecolor:
            Color of errorbars and outliers.
        :param title:
            Title of the plot.
        :param ylabel:
            Label on the y-axis of the main plot.
        :param figsize:
            Size of the figure, including the pull plot.
        :param grid:
            Whether to show grid or not.
        :param n_ticks:
            Number of y-axis ticks to use.
        :param n_ticks_pull:
            Number of y-axis ticks to use in the pull plot.
        :param sigma:
        :param ax:
            Optional ax where to plot the main plot.
        :param pull_ax:
            Optional ax where to plot the pull plot.
        :return:
        """

        if sigma is not None and sigma < 0:
            raise ValueError(
                f"Parameter `sigma` must be non-negative, found `{sigma}`."
            )
        # If ax and pull_ax are none, make a new figure and add the two axes with the proper ratio between them.
        # Otherwise, just use ax and pull_ax.
        if not callable(callback):
            raise TypeError(
                f"Expected `callback` to be callable, found type `{type(callback)}`."
            )

        if ax is None or pull_ax is None:
            fig, (ax, pull_ax) = plt.subplots(
                nrows=2,
                ncols=1,
                gridspec_kw=dict(height_ratios=height_ratios, hspace=0.025),
                figsize=figsize,
                sharex=True,
            )

        # Compute PDF values
        values = callback(self.axes[0].centers) * self.sum() * self.axes[0].widths
        yerr = np.sqrt(self.view())

        # Compute Pulls
        pulls = (self.view() - values) / yerr

        ax.errorbar(
            self.axes[0].centers,
            values,
            yerr=yerr,
            capsize=1,
            ecolor=ecolor,
            color=color,
            fmt="-",
            capthick=2,
            elinewidth=2,
            zorder=3,  # because of grid
            linewidth=3,
        )
        ax.grid(grid, linestyle="--")

        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.xaxis.set_ticks_position("none")
        ax.set_yticks(np.linspace(np.nanmin(values), np.nanmax(values), n_ticks or 10))

        pull_ax.set_ylabel("Pull")
        pull_ax.set_xlabel(self.axes[0].name)

        maxx = int(np.ceil(np.nanmax(np.abs(pulls))))
        pull_ax.set_yticks(np.linspace(-maxx, maxx, n_ticks_pull or 5))

        mean, sd = np.nanmean(pulls), np.nanstd(pulls)

        if sigma is not None:
            outliers = (pulls > mean + sigma * sd) | (pulls <= mean - sigma * sd)
            colors = np.repeat(color, len(self.axes[0].centers))
            colors[outliers] = ecolor
            pull_ax.hlines(
                mean,
                xmin=self.axes[0].centers[0],
                xmax=self.axes[0].centers[-1],
                color=color,
            )
            pull_ax.hlines(
                mean - sigma * sd,
                xmin=self.axes[0].centers[0],
                xmax=self.axes[0].centers[-1],
                linestyle="--",
                color=color,
            )
            pull_ax.hlines(
                mean + sigma * sd,
                xmin=self.axes[0].centers[0],
                xmax=self.axes[0].centers[-1],
                linestyle="--",
                color=color,
            )
        else:
            colors = color

        pull_ax.bar(self.axes.centers[0], pulls, width=0.1, color=colors, zorder=3)
        pull_ax.grid(grid, linestyle="--")

        return ax, pull_ax
