__author__ = 'Mikhail Vilgelm'


from helperFunctions import TestbedPacket, MeasurementPacket, find_latest_dump
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

            d = pkt.delay  # /pkt.num_hops()

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


if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #    exit("Usage: %s dumpfile" % sys.argv[0])

    folder = gl_dump_path + 'tdma/no-interference-hopping/'

    # p = LogProcessor(folder+find_latest_dump(folder))
    p = LogProcessor(filename=folder+'no_interference_hopping.log')

    print(p.find_motes_in_action())


