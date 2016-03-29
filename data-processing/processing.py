__author__ = 'Mikhail Vilgelm'


from CompressionHelper import TestbedPacket, MeasurementPacket
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import datetime


gl_mote_range = range(1, 14)
gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''


class LogProcessor:
    """
    Defines functionality for processing a dump of WSN packets defined by MeasurementPacket class
    """

    def __init__(self, filename):
        self.filename = filename  # we only store the filename
        self.packets = self.load_packets()

    def yield_line(self):
        """
        Lazy file reading: to avoid loading full file into memory
        :return:
        """
        with open(self.filename, 'r') as f:
            for line in f:
                yield line

    def load_packets(self):
        """
        Load all packets: dangerous if file size is ~ Gbytes
        :return: packets list
        """
        packets = []
        for line in self.yield_line():

            lines = line.split('\t')
            line = lines[0]

            pkt = TestbedPacket.serialize_data(line)

            packets.append(pkt)

        return packets

    def calculate_mean_delay(self):
        """
        :return: average delay
        """
        return np.mean(self.get_delays())


    def get_delays(self, addr):
        """
        Get delay values for every packet belonging to the same src mote with addr
        :return: delay list: delay for every packet in seconds
        """
        delay = []
        for pkt in self.packets:
            if pkt.src_addr != addr:
                continue

            d = pkt.get_delay()  # /pkt.num_hops()

            if d < 0:
                # shouldn't be the case...
                continue

            delay.append(d*15/1000)

        return delay

    def find_motes_in_action(self):
        """
        Get all motes which were active during the recording period
        :return: set of motes sending or forwarding something, as seen from DAG root
        """
        motes = set()
        for line in self.yield_line():
            lines = line.split('\t')
            line = lines[0]

            if line == '[]':
                continue

            pkt = TestbedPacket.serialize_data(line)

            for v in pkt.hop_info:
                src = v['addr']
                if (src not in motes) and (src > 0) and (src <= 20):
                    motes.add(src)

        return motes

    def sort_by_motes(self):
            """
            Sorts packets by the src address
            :return: a list where every element is a list of packets corresponding to a specific mote
            """
            motes = [[] for x in gl_mote_range]

            for pkt in self.packets:
                motes[pkt.src_addr-1].append(pkt)

            return motes

    def get_avg_hops(self, addr):
        """
        Calculate average number of hops
        :return:
        """

        pkt_hops = []
        for pkt in self.packets:
            if pkt.src_addr != addr:
                continue

            if pkt.get_delay() < 0:
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


def find_latest_dump(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))[-1]


if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #    exit("Usage: %s dumpfile" % sys.argv[0])

    folder = gl_dump_path + 'tdma/no-interference-hopping/'

    # p = LogProcessor(folder+find_latest_dump(folder))
    p = LogProcessor(folder+'no_interference_hopping.log')

    print(p.find_motes_in_action())

    p.plot_num_packets(show=False)
    p.plot_timeline(show=False)
    p.plot_delays(show=False)

    # p.plot_delays(normalized=True, show=False)

    p.plot_avg_hops(show=False)
    p.plot_retx(show=False)

    plt.show()


