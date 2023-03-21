import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

font = {'family': 'serif',
        'weight': 'normal',
        'size': 16}


def freedman_diaconis_rule(data):
    """rule to find the bin width and number of bins from data"""
    data = np.array(data)
    if (stats.iqr(data) > 0):
        bin_width = 2 * stats.iqr(data) / len(data) ** (1 / 3)
        Nbins = int(np.ceil((data.max() - data.min()) / bin_width))
        return Nbins, bin_width
    else:
        return 100, 0


def add_text_to_ax(x_coord, y_coord, string, ax, fontsize=12, color='k'):
    """ Shortcut to add text to an ax with proper font. Relative coords."""
    ax.text(x_coord, y_coord, string, family='monospace', fontsize=fontsize,
            transform=ax.transAxes, verticalalignment='top', color=color)
    return None


def apply(timings, xmin=0, xmax=800, **kwargs):
    n = len(timings)
    fig, axs = plt.subplots(nrows=n, ncols=1, figsize=(16, 4 * n))
    i = 0

    for k, v in timings.items():
        Nbins, width = freedman_diaconis_rule(v)
        axs[i].hist(v, range=(xmin, xmax), bins=Nbins)
        axs[i].title.set_text(k)
        if k[0] == 'RESPONSE':
            text = f'MAX Deadline: {np.max(v)}'
        elif k[0] == 'CONDITION':
            text = f'MIN Delay: {np.min(v)}'
        add_text_to_ax(0.45, 0.95, f'{text}|mean:{np.mean(v):.2f}|std:{np.std(v):.2f}|median:{np.median(v):.2f}',
                       axs[i])
        i = i + 1
    return fig, axs
