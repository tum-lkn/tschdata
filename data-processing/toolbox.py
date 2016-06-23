"""
Helper functions and basic data structures for processing of logged packet.
"""
__author__ = 'Mikhail Vilgelm'

import numpy as np
import scipy.stats as st
from pylab import setp

import os
from os.path import isfile, join
from matplotlib import rcParams

def find_latest_dump(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))[-1]


def set_box_plot(bp):
    """
    Set parameters of the given boxplot
    :param bp:
    :return:
    """
    for b in bp['boxes']:
        setp(b, color='blue', linewidth=1.5)
    for c in bp['caps']:
        setp(c, color='black', linewidth=1.5)
    for w in bp['whiskers']:
        setp(w, color='blue', linewidth=1.5)
    for m in bp['medians']:
        setp(m, color='red', linewidth=1.5)
    for o in bp['fliers']:
        setp(o, markersize=8, markeredgewidth=1.5)


def set_box_plot_diff(bp):
    for idx, b in enumerate(bp['boxes']):
        if idx%2 == 1:
            setp(b, color='blue', linewidth=1.5)
        else:
            setp(b, color='red', linewidth=1.5)

    for idx, c in enumerate(bp['caps']):
        setp(c, color='black', linewidth=1.5)

    for idx, w in enumerate(bp['whiskers']):
        if idx % 2 == 1:
            setp(w, color='blue', linewidth=1.5)
        else:
            setp(w, color='red', linewidth=1.5)
    for idx, m in enumerate(bp['medians']):
        # if idx%2 == 1:
        setp(m, color='red', linewidth=1.5)


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), st.sem(a)
    h = se * st.t._ppf((1+confidence)/2., n-1)
    return h


def get_all_files(path, folders=None):

    files = []

    if folders is None:
        folders = [path + 'tdma/', path + 'shared/']
    else:
        folders = [path + folder + '/' for folder in folders]

    for folder in folders:
        temp = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        temp = sorted(temp)
        files += [folder+f for f in temp]

    return files


def set_figure_parameters():
    rcParams.update(
        {'figure.autolayout': True, 'font.size': 14, 'font.family': 'serif', 'font.sans-serif': ['Helvetica']})


if __name__ == '__main__':
    '''
    Testing
    '''
    pass





