"""
Most basic processing and plots from the dump.
Can be used to monitor current network status
"""

__author__ = 'Mikhail Vilgelm'


import os
import matplotlib.pyplot as plt
from os.path import isfile, join
import numpy as np
from matplotlib import gridspec
from pylab import show, savefig, figure, \
                ylim, boxplot, grid

from log_processor import LogProcessor
from toolbox import set_box_plot, set_figure_parameters, get_all_files
import csv


set_figure_parameters()

gl_mote_range = range(1, 33)
# gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'

gl_dump_path = os.getcwd() + '/../'

gl_image_path = os.getenv("HOME") + ''


class BasicProcessor(LogProcessor):
    """
    Defines the basic analysis tools and plots of the log: retransmissions, delay, reliabiltiy...
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def plot_retx(self):
        """
        Plot the distribution of the retransmission counter for all packets
        :return:
        """

        retx = []
        for pkt in self.packets:
            for hop in pkt.hop_info:
                if hop['retx'] != 0:
                    retx.append(hop['retx'])

        plt.figure()
        plt.hist(retx)

    def plot_delay_per_mote(self, addr):
        """
        Plot the delay distribution for motes
        :return:
        """
        plt.figure()
        plt.boxplot(self.get_delays(addr))
        plt.grid(True)

    def plot_delays(self):
        """
        Plot delay distribution for all motes
        :return:
        """
        plt.figure()
        delays = []
        for addr in gl_mote_range:
            delays.append(self.get_delays(addr))
        plt.boxplot(delays, showmeans=True)

        plt.ylim((0, 2))

        plt.ylabel('delay, s')
        plt.xlabel('mote #')
        plt.grid(True)

        # return means
        return [np.mean(d) for d in delays if len(d) > 0]

    def get_all_delays(self, motes=gl_mote_range, normalized=False):
        """
        Retrieve all delays sorted by the source mote id
        :return:
        """
        delays = []
        for addr in motes:
            delays += self.get_delays(addr, normalized)

        return delays

    def plot_avg_hops(self):
        """
        Plot the distribution of the number of hops for all packets for all motes.
        :return:
        """

        plt.figure()
        hops = []
        for addr in gl_mote_range:
            hops.append(self.get_avg_hops(addr))
        plt.boxplot(hops)

        plt.ylim((0, 5))

        plt.ylabel('hops')
        plt.xlabel('mote #')

    def plot_timeline(self, writer=None):
        """
        Plot a timeline of the measurements for every mote: ASN of the packet generation vs.
        its application sequence number. Can be used to check whether any mote died during the measurements or
        was reset.
        :param writer: write the sequence numbers to the file
        :return:
        """

        motes = self.sort_by_motes()

        plt.figure()

        for idx, mote in enumerate(motes):
            if not writer is None:
                writer.writerow([pkt.seqN for pkt in mote])
            plt.plot([pkt.seqN for pkt in mote], [pkt.asn_first for pkt in mote], label='#%d' % (idx+1, ))
            # plt.plot([pkt.seqN for pkt in mote], label='#%d' % (idx + 1,))

        plt.xlabel('seqN')
        plt.ylabel('asn')
        plt.legend(loc=0)
        plt.grid(True)

    def plot_num_packets(self):
        """
        Plot number of received packets for every mote.
        :return:
        """

        motes = self.sort_by_motes()

        plt.figure()

        plt.bar(gl_mote_range, [len(mote) for mote in motes])

        plt.xlabel('mote #')
        plt.ylabel('num packets received')

        plt.grid(True)

    def plot_reliability(self, return_result=False):
        """
        Plot application layer reliability for all motes.
        :param return_result:
        :return:
        """

        motes = self.sort_by_motes()

        success = []

        weights = []

        for mote in motes:
            # convert to set
            if len(mote) == 0:
                continue

            seen_sqns = set([pkt.seqN for pkt in mote])
            max_sqn = max(seen_sqns)
            min_sqn = min(seen_sqns)
            pdr = len(seen_sqns)/(max_sqn-min_sqn+1)

            success.append(pdr)
            weights.append(max_sqn-min_sqn)

            print('Max seqn: %d, min seqn: %d, distinct packets: %d' % (max_sqn, min_sqn, len(seen_sqns)))
            print('PDR: %.5f' % pdr)

        print('Average PDR: %.5f' % np.mean(success))

        sum_weights = sum(weights)
        weights = [w/sum_weights for w in weights]

        weighted_avg = sum([weights[idx]*s for idx, s in enumerate(success)])


        if return_result:
            return success, weighted_avg
        else:
            # plt.figure()
            mote_range = [mote_id for idx, mote_id in enumerate(gl_mote_range) if idx % 2 == 0]
            plt.plot(success, label=self.filename.split("/")[-1].split(".log")[0], marker="^")


def plot_normalized_delay_per_application():
    """
    Plot delay for scenario / application: normalized per hop
    :return:
    """

    # --- folder one --- #
    folder = os.getcwd() + '/../' + 'tdma/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d_tdma = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d_tdma.append(p.get_all_delays(motes=[2, 3, 4, 5, 6, 7, 8], normalized=True))
        d_tdma.append(p.get_all_delays(motes=[9, 10, 11], normalized=True))

    # --- folder two --- #
    folder = os.getcwd() + '/../' + 'shared/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d_shared = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d_shared.append(p.get_all_delays(motes=[2, 3, 4, 5, 6, 7, 8], normalized=True))
        d_shared.append(p.get_all_delays(motes=[9, 10, 11], normalized=True))

    # --- folder two --- #

    fig = plt.figure(figsize=(7.5, 5.7))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    ax0 = fig.add_subplot(gs[0])
    bp_tdma = ax0.boxplot(d_tdma, showmeans=True, showfliers=False)

    x_axis = list(range(9))
    labels = ['', 'I(P)', 'I(B)', 'II(P)', 'II(B)', 'III(P)', 'III(B)', 'IV(P)', 'IV(B)']
    plt.xticks(x_axis, labels)

    # ylim((0, 4))
    grid(True)

    # plt.xlabel('Data set')
    plt.ylabel('Delay, s')

    set_box_plot(bp_tdma)

    ax1 = fig.add_subplot(gs[1])
    bp_shared = ax1.boxplot(d_shared, showmeans=True, showfliers=False)

    # ylim((0, 0.2))
    grid(True)

    # plt.xlabel('Data set')
    labels = ['', 'V(P)', 'V(B)', 'VI(P)', 'VI(B)', 'VII(P)', 'VII(B)', 'VIII(P)', 'VIII(B)']
    plt.xticks(x_axis, labels)

    plt.ylabel('Delay, s')

    set_box_plot(bp_shared)

    savefig('../../SGMeasurements/pics/app_delay.pdf', format='pdf', bbox='tight')
    show()


def plot_all_retx():
    """

    :return:
    """
    for folder in ['../tdma/', '../shared/']:
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        files = sorted(files)
        for filename in files:
            p = BasicProcessor(filename=folder+filename)
            p.plot_retx()
    plt.show()


def plot_all_delays(cdf=False):
    """
    Plot delay for all packets, on the scenario basis
    :return:
    """
    # --- folder one --- #
    folder = os.getcwd() + '/../' + 'tdma/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d.append(p.get_all_delays())

    # --- folder two --- #
    folder = os.getcwd() + '/../' + 'shared/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d.append(p.get_all_delays())

    # --- folder two --- #

    if not cdf:

        figure(figsize=(7.5, 4))

        bp = boxplot(d, showmeans=True, showfliers=False)

        ylim((0, 2.5))
        grid(True)

        x_axis = list(range(9))
        labels = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
        plt.xticks(x_axis, labels)

        plt.xlabel('Data set')
        plt.ylabel('End-to-end delay, s')

        set_box_plot(bp)

        savefig('../../sgpaper/pics/all_delay.pdf', format='pdf', bbox='tight')
        show()
    else:

        figure(figsize=(7.5, 4))

        for data_set in d:

            ecdf = sm.distributions.ECDF(data_set)

            x = np.linspace(min(data_set), max(data_set))
            y = ecdf(x)

            plt.step(x, y)

            plt.xlim((0, 2.5))

        plt.show()


def plot_all_reliabilities():
    """
    Plot packet delivery ratio for all data sets
    :return:
    """
    rel = []
    avg = []
    f = open('seqn.csv', 'a+')
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)

    for filename in get_all_files(gl_dump_path):
        p = BasicProcessor(filename=filename)
        p.correct_timeline(clean_all=False)
        p.plot_timeline(writer=wr)
        r, w = p.plot_reliability(return_result=True)
        rel.append(r)
        avg.append(w)

    f.close()

    plt.figure(figsize=(7.5, 3.5))
    bp = plt.boxplot(rel, flierprops={'linewidth':1.5}, showmeans=True)

    plt.hlines(0.95, xmin=0, xmax=9, linestyles='--', linewidth=1, label='0.95')
    x_axis = list(range(9))
    labels = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']

    plt.xticks(x_axis, labels)
    plt.grid(True)
    plt.ylim((0.35, 1.1))
    plt.legend(loc=4)

    plt.ylabel('PDR')

    set_box_plot(bp)

    # plt.savefig('../../sgpaper/pics/rel3_mikhail.pdf', format='pdf', bbox='tight')
    plt.show()


def test_multichannel():
    """
    Test basic performance parameters for whitening measurements
    :return:
    """

    set_figure_parameters()
    plt.figure()

    for i in range(1, 5):
        p = BasicProcessor(filename="../../../whitening/WHData/Data/triagnosys/%d.log" % i,
                       format="WHITENING")

        # p.plot_avg_hops()
        # p.plot_delays()

        # p.plot_timeline()

        # p.correct_timeline(clean_all=False)
        p.plot_reliability()

    plt.ylim((0.0, 1.1))
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    # plot_all_delays()
    # plot_all_reliabilities()
    test_multichannel()
    # plot_normalized_delay_per_application()
    # plot_all_retx()





