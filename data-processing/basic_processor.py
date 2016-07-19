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
from tsch_hopping_calculator import TSCHopping
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

    def plot_motes_reliability(self, return_result=False):
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

    def plot_channels_reliability(self, schedule_folder):
        """
        TODO better representation
        :param schedule_folder:
        :return:
        """

        a = TSCHopping(schedule_folder)

        channel_drops_cnt = [0] * 16
        channel_usage_cnt = [0] * 16
        big_error = 0
        for pkt in self.packets:
            for hop in pkt.hop_info:
                if hop['freq'] > 26 or hop['freq'] < 11:
                    big_error += 1
                else:
                    if hop['retx'] != 0: #and hop['retx'] != 4:
                        channel_usage_cnt[hop['freq'] - 11] += 1
                        for i in range(1,4-hop['retx']+1):
                            d_freq = a.calculate_dropped_frequency(hop['addr'],i,pkt.asn_last)
                            channel_drops_cnt[d_freq - 11] += 1
                            channel_usage_cnt[d_freq - 11] += 1


        #channel_drops_cnt = [ channel_drop/max(channel_drops_cnt) for channel_drop in channel_drops_cnt]
        channel_drops_cnt = [channel_drop / (channel_usage_cnt[i]+1) for i,channel_drop in enumerate(channel_drops_cnt)]
        print(channel_drops_cnt)
        print("There are %d out of range frequencies out of %d packets" % (big_error, len(self.packets)))
        plt.figure()
        plt.plot(channel_drops_cnt)
        return


    def plot_hopping(self, schedule_folder):

        theoretical_freq, measured_freq = self.check_hopping(schedule_folder)

        # Todo how to do this??? Plot multiple curves on a single figure
        # plt.figure()
        # plt.plot(theoretical_freq)
        # plt.plot(measured_freq)

        return


if __name__ == '__main__':
    pass





