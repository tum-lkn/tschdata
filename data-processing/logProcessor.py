"""
Main module for log processing
"""
__author__ = 'Mikhail Vilgelm'


from helperFunctions import TestbedPacket, MeasurementPacket, find_latest_dump
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import timedelta
import json


gl_mote_range = range(1, 14)
gl_dump_path = os.getcwd() + '/../'
# gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'
gl_image_path = os.getenv("HOME") + ''


class LogProcessor:
    """
    Defines functionality for processing a dump of WSN packets defined by MeasurementPacket class
    """

    def __init__(self, filename):
        print('Creating a processor for %s' % filename)
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
            timestamp = lines[1].split('\n')[0]

            pkt = TestbedPacket.load_data(line, timestamp)

            packets.append(pkt)

        return packets

    def calculate_mean_delay(self):
        """
        :return: average delay
        """
        return np.mean(self.get_delays())


    def get_delays(self, addr, normalized=False):
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

            if normalized:
                d = d/pkt.num_hops()

            delay.append(d)

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
            timestamp = lines[1].split('\n')[0]

            if line == '[]':
                continue

            pkt = TestbedPacket.load_data(line, timestamp)

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

    def write_as_json(self, output):

        f = open(output, 'w')
        f.write('{'+'\"packets\":'+'[')
        for idx, pkt in enumerate(self.packets):
            print(pkt.serialize())
            if idx != (len(self.packets)-1):
                f.write(str(pkt.serialize()).replace('\'', '\"')+',')
            else:
                f.write(str(pkt.serialize()).replace('\'', '\"')+']}')

        f.close()



if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #    exit("Usage: %s dumpfile" % sys.argv[0])

    folder = gl_dump_path  + 'tdma'

    # p = LogProcessor(folder+find_latest_dump(folder))
    p = LogProcessor(filename=folder+'/no-interference-hopping/interference_hopping.log')

    print(p.find_motes_in_action())

    p.write_as_json('../json/tdma_interference.json')

    with open('../json/tdma_interference.json') as json_data:
        a = json.load(json_data)

    print('finished loading... ')
    print(a['packets'][0])

