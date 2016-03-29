"""
Most basic processing and plots from the dump.
Can be used to monitor current network status
"""

__author__ = 'Mikhail Vilgelm'


import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import datetime

from logProcessor import LogProcessor
from helperFunctions import find_latest_dump

gl_mote_range = range(1, 14)
# gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'
gl_dump_path = os.getcwd() + '/../' + 'tdma/no-interference-hopping/'
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

    def plot_retx(self, show=True):

        retx = []
        for pkt in self.packets:
            for hop in pkt.hop_info:
                if hop['retx'] != 0:
                    retx.append(hop['retx'])

        plt.figure()
        plt.hist(retx)
        if show:
            plt.show()

    def plot_delay(self, addr, show=True):
        """

        :return:
        """
        plt.figure()
        plt.boxplot(self.get_delays(addr))
        plt.grid(True)
        if show:
            plt.show()


    def plot_delays(self, show=True):
        """

        :return:
        """
        plt.figure()
        delays = []
        for addr in gl_mote_range:
            delays.append(self.get_delays(addr))
        plt.boxplot(delays)

        plt.ylabel('delay, s')
        plt.xlabel('mote #')
        plt.grid(True)

        if show:
            plt.show()


    def plot_avg_hops(self, show=True):
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

        if show:
            plt.show()



    def plot_timeline(self, show=True):

        motes = self.sort_by_motes()

        plt.figure()

        for idx, mote in enumerate(motes):
            plt.plot([pkt.seqN for pkt in mote], [pkt.asn_first for pkt in mote], label='#%d' % (idx+1, ))
            # plt.plot([pkt.asn_first for pkt in mote])

        plt.xlabel('seqN')
        plt.ylabel('asn')
        plt.legend(loc=0)
        plt.grid(True)

        if show:
            plt.show()

    def plot_num_packets(self, show=True):

        motes = self.sort_by_motes()

        plt.figure()

        plt.bar(gl_mote_range, [len(mote) for mote in motes])

        plt.xlabel('mote #')
        plt.ylabel('num packets received')

        plt.grid(True)

        if show:
            plt.show()



if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #    exit("Usage: %s dumpfile" % sys.argv[0])

    folder = gl_dump_path

    # p = LogProcessor(folder+find_latest_dump(folder))
    p = BasicProcessor(filename=folder+'interference_hopping.log')#find_latest_dump(folder))


    print(p.find_motes_in_action())

    p.plot_num_packets(show=False)
    p.plot_timeline(show=False)
    p.plot_delays(show=False)

    # p.plot_delays(normalized=True, show=False)

    p.plot_avg_hops(show=False)
    p.plot_retx(show=False)

    plt.show()
