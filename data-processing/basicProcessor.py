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
from topologyProcessor import TopologyLogProcessor

gl_mote_range = range(1, 14)
# gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'
gl_dump_path = os.getcwd() + '/../' + 'shared/'
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

        plt.ylim((0, 5))

        plt.ylabel('delay, s')
        plt.xlabel('mote #')
        plt.grid(True)

        # return means
        return [np.mean(d) for d in delays if len(d) > 0]

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

    def plot_app_drop_rate(self):
        pass
        for mote in self.sort_by_motes():
            pass




if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #    exit("Usage: %s dumpfile" % sys.argv[0])

    folder = gl_dump_path

    # filename = folder+find_latest_dump(folder)
    filename=folder+'no_interference.log'
    print('Creating a processor for %s' % filename)

    p = BasicProcessor(filename=filename)

    print(p.find_motes_in_action())

    p.plot_num_packets()
    p.plot_timeline()
    means_without = p.plot_delays()
    p.plot_avg_hops()
    p.plot_retx()


    filename=folder+'induced_interference.log'
    print('Creating a processor for %s' % filename)

    p = BasicProcessor(filename=filename)

    print(p.find_motes_in_action())

    p.plot_num_packets()
    p.plot_timeline()
    means_with = p.plot_delays()
    p.plot_avg_hops()
    p.plot_retx()

    print(['%.2f' % (y/x, ) for x, y in zip(means_without, means_with)])

    plt.show()




