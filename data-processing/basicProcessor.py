"""
Most basic processing and plots from the dump.
Can be used to monitor current network status
"""

__author__ = 'Mikhail Vilgelm'


import os
import matplotlib.pyplot as plt
from os.path import isfile, join
import numpy as np
import sys
import datetime
from matplotlib import gridspec
from pylab import plot, show, savefig, xlim, figure, \
                hold, ylim, legend, boxplot, setp, axes, grid

from logProcessor import LogProcessor
from helperFunctions import find_latest_dump, set_box_plot, set_figure_parameters, get_all_files
from topologyProcessor import TopologyLogProcessor


set_figure_parameters()

gl_mote_range = range(1, 14)
# gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'

gl_dump_path = os.getcwd() + '/../'

gl_image_path = os.getenv("HOME") + ''


class BasicProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_avg_hops(self, addr):
        """
        Calculate average number of hops
        :return:
        """

        pkt_hops = []
        for pkt in self.packets:
            if pkt.src_addr != addr:
                continue

            if pkt.delay < 0:
                print(pkt.asn_last)
                print(pkt.asn_first)
                # erroneous packet
                continue

            num_hops = 0
            for hop in pkt.hop_info:
                if hop['addr'] != 0:
                    num_hops += 1
            pkt_hops.append(num_hops)

        return pkt_hops

    def plot_retx(self):

        retx = []
        for pkt in self.packets:
            for hop in pkt.hop_info:
                if hop['retx'] != 0:
                    retx.append(hop['retx'])

        plt.figure()
        plt.hist(retx)


    def plot_delay(self, addr):
        """

        :return:
        """
        plt.figure()
        plt.boxplot(self.get_delays(addr))
        plt.grid(True)



    def plot_delays(self):
        """

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

        :return:
        """
        delays = []
        for addr in motes:
            delays += self.get_delays(addr, normalized)

        # return means
        return delays

    def plot_avg_hops(self):
        """

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

    def correct_timeline(self, clean_all=False):

        motes = self.sort_by_motes()

        if clean_all:
            motes_clean = [[] for _ in gl_mote_range]

        for idx, mote in enumerate(motes):
            if len(mote) == 0:
                continue

            last_seen_pkt = None
            seqn_correction = 0

            for pkt in mote:
                if last_seen_pkt is None:
                    last_seen_pkt = pkt

                pkt.seqN += seqn_correction

                if (pkt.seqN < last_seen_pkt.seqN) and (pkt.asn_first > last_seen_pkt.asn_first):
                    print('Mote %d, reset detected at %d' % (idx+1, pkt.asn_first))
                    pkt.seqN -= seqn_correction  # previous correction was falsely done, cancel it
                    seqn_correction = last_seen_pkt.seqN
                    pkt.seqN += seqn_correction
                    if clean_all:
                        break

                if clean_all:
                    motes_clean[idx].append(pkt)

                last_seen_pkt = pkt

        if clean_all:
            for mote in motes_clean:
                self.packets += mote

    def plot_timeline(self):

        motes = self.sort_by_motes()

        plt.figure()

        for idx, mote in enumerate(motes):
            plt.plot([pkt.seqN for pkt in mote], [pkt.asn_first for pkt in mote], label='#%d' % (idx+1, ))
            # plt.plot([pkt.asn_first for pkt in mote])

        plt.xlabel('seqN')
        plt.ylabel('asn')
        plt.legend(loc=0)
        plt.grid(True)

    def plot_num_packets(self):

        motes = self.sort_by_motes()

        plt.figure()

        plt.bar(gl_mote_range, [len(mote) for mote in motes])

        plt.xlabel('mote #')
        plt.ylabel('num packets received')

        plt.grid(True)

    def plot_reliability(self, return_result=False):

        motes = self.sort_by_motes()

        success = []

        for mote in motes:
            # convert to set
            if len(mote) == 0:
                continue

            seen_sqns = set([pkt.seqN for pkt in mote])
            max_sqn = max(seen_sqns)
            min_sqn = min(seen_sqns)
            count_loss = 0
            for i in range(min_sqn, max_sqn+1):
                if not i in seen_sqns:
                    count_loss += 1
            pdr = (max_sqn - min_sqn - count_loss)/(max_sqn-min_sqn)
            success.append(pdr)
            print('PDR: %.2f' % pdr)

        print('Average PDR: %.2f' % np.mean(success))

        if return_result:
            return success
        else:
            plt.figure()
            plt.plot(gl_mote_range, success)




    def plot_app_drop_rate(self):
        pass
        for mote in self.sort_by_motes():
            pass


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

    fig = plt.figure(figsize=(7.5, 6))
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

    savefig('../../sgpaper/pics/app_delay.pdf', format='pdf', bbox='tight')
    show()


def plot_all_retx():
    for folder in ['../tdma/', '../shared/']:
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        files = sorted(files)
        for filename in files:
            p = BasicProcessor(filename=folder+filename)
            p.plot_retx()
    plt.show()




def plot_all_delays():
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

    figure(figsize=(7.5, 4))

    bp = boxplot(d, showmeans=True, showfliers=False)

    ylim((0, 2.5))
    grid(True)

    x_axis = list(range(9))
    labels = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
    plt.xticks(x_axis, labels)

    plt.xlabel('Data set')
    plt.ylabel('Delay, s')

    set_box_plot(bp)

    savefig('../../sgpaper/pics/all_delay.pdf', format='pdf', bbox='tight')
    show()


if __name__ == '__main__':

    rel = []
    for filename in get_all_files(gl_dump_path):
        p = BasicProcessor(filename=filename)
        p.correct_timeline(clean_all=False)
        p.plot_timeline()
        rel.append(p.plot_reliability(return_result=True))

    plt.figure()
    plt.boxplot(rel, showmeans=True)
    plt.show()
    # plot_all_delays()
    # plot_normalized_delay_per_application()
    # plot_all_retx()





