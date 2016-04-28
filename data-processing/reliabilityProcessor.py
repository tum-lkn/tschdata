__author__ = 'Mikhail Vilgelm'

import pandas as pd
import math
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
import operator
from matplotlib import gridspec
# import seaborn.apionly
import seaborn

from delayProcessor import DelayLogProcessor

seaborn.set_style("whitegrid", {'figure.autolayout': True, 'font.size': 16, 'font.family': 'serif',
                                'font.sans-serif': ['Helvetica'], 'grid.linestyle': u'--', 'axes.edgecolor': '0.2'})

# from matplotlib import rcParams
# rcParams.update({'figure.autolayout': True, 'font.size': 14, 'font.family': 'serif', 'font.sans-serif': ['Helvetica']})

def prod(iterable):
    return reduce(operator.mul, iterable, 1)

gl_best_links = '../matlab-murat/destinations.csv'
gl_reliability = '../matlab-murat/reliability.csv'

class ReliabilityProcessor():

    def __init__(self):
        # read the reliability data
        self.links_df = pd.read_csv(gl_best_links, names=list(range(1, 14)))
        self.reliability_df = pd.read_csv(gl_reliability, names=list(range(1, 14)))

        # average reliability... (we don't care about channels)
        self.reliability_df['set'] = pd.Series([math.floor(i/16) for i in range(128)], index=self.reliability_df.index)
        self.reliability_df = self.reliability_df.groupby('set').mean()

        # replace all unused/unexisting links with nan
        self.links_df = self.links_df.replace(0, float('nan'))
        self.reliability_df = self.reliability_df.replace(float(0), float('nan'))

        # construct reliability map
        self.reliability_map = pd.DataFrame(index=list(range(1, 105)), columns=list(range(1, 14)))
        self.reliability_map['set'] = pd.Series([math.floor(i/13) for i in range(104)], index=self.reliability_map.index)

        # for all datasets:
        for ds in range(8):
            for mote in range(1, 14):
                col = mote  # source
                index = ds*13 + self.links_df[mote][ds]  # destination
                value = self.reliability_df[mote][ds]
                self.reliability_map.set_value(index, col, value)

        # print(self.reliability_map)

    def get_path_reliability(self, data_set, path):
        set_reliability = self.reliability_map[self.reliability_map['set'] == data_set]

        path_rel = []

        for idx, hop in enumerate(path):
            # assume every path has mote 1 after the last hop
            src = hop
            if idx != len(path)-1:
                dst = path[idx+1]
            else:
                dst = 1
            try:
                link_rel = set_reliability[src][dst + data_set*13]
            except:
                print('src:%d, dst:%d' % (src, dst))
                print(set_reliability)
                pass

            if np.isnan(link_rel):
                return -1
            else:
                path_rel.append(link_rel)

        return path_rel


gl_reliability_map = ReliabilityProcessor()

gl_data_set = {'tdma/no_interference.log': 0,
               'tdma/interference.log': 1,
               'tdma/induced_interference.log': 2,
               'tdma/high_load.log': 3,
               'shared/no_interference.log': 4,
               'shared/interference.log': 5,
               'shared/induced_interference.log': 6,
               'shared/high_load.log': 7}


def delay_reliabiltiy_correlation(logfile):

    print(logfile.split('../')[-1])
    ds = gl_data_set[logfile.split('../')[-1]]

    dp = DelayLogProcessor(filename=logfile)
    paths, _ = dp.get_all_paths_w_delay()

    path_rel_df = pd.DataFrame(index=list(range(len(paths))), columns=['path', 'reliability', 'delay'])

    print(len(paths))

    for idx, path in enumerate(paths):
        p = path[0]  # take the actual path
        p_rel = gl_reliability_map.get_path_reliability(ds, p)
        # add to dataframe
        index = idx
        path_rel_df.set_value(index, 'path', p)  # add path
        path_rel_df.set_value(index, 'reliability', p_rel)  # add reliability
        # add normalized delay
        path_rel_df.set_value(index, 'delay', [d/len(p) for d in path[1]])
        # add delay
        # path_rel_df.set_value(index, 'delay', path[1])

    # filter out paths with no reliability data
    path_rel_df = path_rel_df[path_rel_df['reliability'] != -1]


    # plt.figure()
    return path_rel_df

def plot_mean_vs_path_length(path_data):
    """
    Plot average delay on the path vs. average link reliability on the path
    :param path_data:
    :return:
    """
    # effective path reliability value
    path_data['path_length'] = path_data['reliability'].apply(len)
    # mean delay
    path_data['delay'] = path_data['delay'].apply(np.var)

    path_rel_df = path_data.sort_values('path_length')

    print(path_rel_df)

    lm_original = np.polyfit(path_rel_df.path_length, path_rel_df.delay, 1)

    # calculate the y values based on the co-efficients from the model
    r_x, r_y = zip(*((i, i*lm_original[0] + lm_original[1]) for i in path_rel_df.path_length))

    # Put in to a data frame, to keep is all nice
    lm_original_plot = pd.DataFrame({
    'path_length' : r_x,
    'delay' : r_y
    })

    # plt.figure()
    plt.plot(path_rel_df.path_length, path_rel_df.delay, 'bo', label='path reliability')
    plt.plot(lm_original_plot.path_length, lm_original_plot.delay, 'r-')
    # lm_original_plot.plot(kind='line', color='Red')
    # plt.show()


def plot_mean_vs_mean(path_data):
    """
    Plot average delay on the path vs. average link reliability on the path
    :param path_data:
    :return:
    """
    # effective path reliability value
    path_data['reliability'] = path_data['reliability'].apply(np.mean)
    # mean delay
    path_data['delay'] = path_data['delay'].apply(np.mean)

    path_rel_df = path_data.sort_values('reliability')

    print(path_rel_df)



    # plt.figure()
    plt.plot(path_rel_df['reliability'], path_rel_df['delay'], 'rs', label='mean link reliability')
    # plt.show()


def plot_mean_vs_prod(path_data, ax, marker='bo'):
    """
    Plot mean of the delay vs path reliability
    :param path_data:
    :param marker:
    :return:
    """
    # effective path reliability value
    path_data['reliability'] = path_data['reliability'].apply(np.prod)
    # mean delay
    path_data['delay'] = path_data['delay'].apply(np.mean)

    path_rel_df = path_data.sort_values('reliability')

    print(path_rel_df)

    lm_original = np.polyfit(path_rel_df.reliability, path_rel_df.delay, 1)

    # calculate the y values based on the co-efficients from the model
    r_x, r_y = zip(*((i, i*lm_original[0] + lm_original[1]) for i in path_rel_df.reliability))

    # Put in to a data frame, to keep is all nice
    lm_original_plot = pd.DataFrame({
    'reliability' : r_x,
    'delay' : r_y
    })

    ax.plot(path_rel_df.reliability, path_rel_df.delay, marker)
    ax.plot(lm_original_plot.reliability, lm_original_plot.delay, 'r-')


def plot_variance_vs_prod(path_data, marker='bo'):
    """
    Plot variance of delay vs path reliability
    :param path_data:
    :param marker:
    :return:
    """
    # effective path reliability value
    path_data['reliability'] = path_data['reliability'].apply(np.prod)
    # mean delay
    path_data['delay'] = path_data['delay'].apply(np.var)

    path_rel_df = path_data.sort_values('reliability')

    print(path_rel_df)

    lm_original = np.polyfit(path_rel_df.reliability, path_rel_df.delay, 1)

    # calculate the y values based on the co-efficients from the model
    r_x, r_y = zip(*((i, i*lm_original[0] + lm_original[1]) for i in path_rel_df.reliability))

    # Put in to a data frame, to keep is all nice
    lm_original_plot = pd.DataFrame({
    'reliability' : r_x,
    'delay' : r_y
    })

    # plt.figure()
    plt.plot(path_rel_df.reliability, path_rel_df.delay, marker, label='path reliability')
    plt.plot(lm_original_plot.reliability, lm_original_plot.delay, 'r-')
    # lm_original_plot.plot(kind='line', color='Red')
    # plt.show()



def plot_mean_vs_min(path_data):
    # effective path reliability value
    path_data['reliability'] = path_data['reliability'].apply(np.min)
    # mean delay
    path_data['delay'] = path_data['delay'].apply(np.mean)

    path_rel_df = path_data.sort_values('reliability')

    print(path_rel_df)

    # plt.figure()
    plt.plot(path_rel_df['reliability'], path_rel_df['delay'], 'gs', label='min vs mean')
    # plt.show()


def plot_all_data(callback=plot_mean_vs_path_length):
    """
    Plot for all data
    :return:
    """
    fig = plt.figure(figsize=(7.5, 6))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    data_tdma = []

    folder = '../tdma/'

    logfile = folder + 'no_interference.log'
    data_tdma.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'interference.log'
    data_tdma.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'induced_interference.log'
    data_tdma.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'high_load.log'
    data_tdma.append(delay_reliabiltiy_correlation(logfile))

    result_tdma = pd.concat(data_tdma)

    ax0 = fig.add_subplot(gs[0])
    callback(result_tdma, ax0)

    plt.ylim((0, 3))
    plt.ylabel('Delay, s')
    # plt.xlabel('Path reliabiltiy')

    # plt.figure()

    data_shared = []

    folder = '../shared/'

    logfile = folder + 'no_interference.log'
    data_shared.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'interference.log'
    data_shared.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'induced_interference.log'
    data_shared.append(delay_reliabiltiy_correlation(logfile))

    logfile = folder + 'high_load.log'
    data_shared.append(delay_reliabiltiy_correlation(logfile))

    result_shared = pd.concat(data_shared)

    # plot_mean_vs_prod(result_shared)
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    callback(result_shared, ax1)

    plt.ylim((0.0, 0.14))
    plt.ylabel('Delay, s')
    plt.xlabel('Path reliability')

    plt.tight_layout()
    plt.savefig('../../sgpaper/pics/path_delay_vs_reliability.pdf', format='pdf', bbox='tight')
    plt.show()



if __name__ == '__main__':

    plot_all_data(plot_mean_vs_prod)









