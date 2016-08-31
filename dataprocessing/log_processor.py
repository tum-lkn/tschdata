"""
Main module for log processing
"""
import os, sys
import numpy as np

from dataprocessing.uinject_packet import TestbedPacket
from dataprocessing.tsch_hopping_calculator import TSCHopping


gl_mote_range = range(1, 34)
gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''


class LogProcessor:
    """
    Defines the main functionality for processing a dump of WSN packets defined by MeasurementPacket class.
    Only basic functionality is contained in this class, plotting and advanced functions are in the subclasses
    """

    def __init__(self, filename, format="SMARTGRID"):
        print('Creating a processor for %s' % filename)
        self.filename = filename  # we only store the filename
        self.packets = self.load_packets(format)

    def yield_line(self):
        """
        Lazy file reading: to avoid loading full file into memory
        :return:
        """
        with open(self.filename, 'r') as f:
            for line in f:
                yield line

    def load_packets(self, format):
        """
        Load all packets: dangerous if file size is ~ Gbytes
        :return: packets list
        """
        packets = []
        i=0
        for line in self.yield_line():
            i+=1
            if format == "WHITENING":
                lines = line.split("] ")

                if len(lines) < 2:
                    lines = line.split("]\t")
                    if len(lines) < 2:
                        print("Unrecoverable parse error")

                line = lines[0] + "]"

                timestamp = lines[1].split('\n')[0]
            else:
                lines = line.split('\t')
                line = lines[0]

                timestamp = lines[1].split('\n')[0]

            pkt = TestbedPacket.load_data(line, timestamp, format)

            packets.append(pkt)

        return packets

    def calculate_mean_delay(self, addr):
        """
        Average delay for all packets from given addr
        :return: average delay
        """
        return np.mean(self.get_delays(addr))

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
                raise RuntimeError

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
        """
        Save the file in json format
        :param output: filename to save
        :return:
        """

        f = open(output, 'w')
        f.write('{'+'\"packets\":'+'[')
        for idx, pkt in enumerate(self.packets):
            print(pkt.serialize())
            if idx != (len(self.packets)-1):
                f.write(str(pkt.serialize()).replace('\'', '\"')+',')
            else:
                f.write(str(pkt.serialize()).replace('\'', '\"')+']}')

        f.close()

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

    def correct_timeline(self, clean_all=False):
        """
        Correct the resetting of the application sequence numbers (caused by the resetting of the motes).
        Generation instants (ASN) is used for detecting the reset.
        :param clean_all: do not consider any packets after the first reset
        :return:
        """

        motes = self.sort_by_motes()

        if clean_all:
            motes_clean = [[] for _ in gl_mote_range]

        for idx, mote in enumerate(motes):
            if len(mote) == 0:
                continue

            highest_seen_sqn_pkt = None
            seqn_correction = 0

            for pkt in mote:
                if highest_seen_sqn_pkt is None:
                    highest_seen_sqn_pkt = pkt

                pkt.seqN += seqn_correction

                if (pkt.seqN < highest_seen_sqn_pkt.seqN) and (pkt.asn_first > highest_seen_sqn_pkt.asn_first):
                    print('Mote %d, reset detected at %d' % (idx+1, pkt.asn_first))
                    pkt.seqN -= seqn_correction  # previous correction was falsely done, cancel it

                    seqn_correction = highest_seen_sqn_pkt.seqN

                    pkt.seqN += seqn_correction
                    if clean_all:
                        break

                if clean_all:
                    motes_clean[idx].append(pkt)

                if pkt.seqN > highest_seen_sqn_pkt.seqN:
                    highest_seen_sqn_pkt = pkt

        if clean_all:
            for mote in motes_clean:
                self.packets += mote

    def get_number_of_packets(self):
        """
        :return: number of packets in the data set
        """
        return len(self.packets)

    def get_total_duration(self):
        """
        :return: Duration of the experiment
        """
        t0 = self.packets[0].asn_first
        t1 = self.packets[-1].asn_last
        return (t1-t0)*0.015  # in seconds

    def get_seen_nodes(self):
        """
        :return: map with nodes and number of their occurences.
        """
        seen_nodes = set()
        node_occurrences = {}

        for pkt in self.packets:
            for node in pkt.get_path(full=False):
                if not (node in seen_nodes):
                    seen_nodes.add(node)
                    node_occurrences[node] = 1
                else:
                    node_occurrences[node] += 1

        return node_occurrences

    def get_seen_channels(self):
        """
        :return: map with channels and number of their occurences
        """
        seen_channels = []
        channels_occurrences = []

        for pkt in self.packets:
            for channel in pkt.get_channels():
                if not (channel in seen_channels):
                    seen_channels.append(channel)
                    channels_occurrences.append(1)
                else:
                    channel_idx = seen_channels.index(channel)
                    channels_occurrences[channel_idx] += 1
        dict = {}
        for channel in seen_channels:
            dict[channel] = channels_occurrences[seen_channels.index(channel)]
        return dict

    def get_seen_links(self, type="occurrences"):
        """

        :param type:
        :return:
        """
        seen_links = []

        if type is "occurrences":
            link_occurrences = []

            for pkt in self.packets:
                path = pkt.get_path(full=True)
                for idx, node in enumerate(path):
                    if idx != len(path) - 1:
                        link = [path[idx], path[idx + 1]]
                        if not (link in seen_links):
                            seen_links.append(link)
                            link_occurrences.append(1)
                        else:
                            link_idx = seen_links.index(link)
                            link_occurrences[link_idx] += 1

            return seen_links, link_occurrences

        elif type is "RSSI":
            link_rssi = []

            for pkt in self.packets:
                path = pkt.get_path(full=True)
                RSSIs = pkt.get_rssi()
                for idx, node in enumerate(path):
                    if idx != len(path) - 1:
                        link = [path[idx], path[idx + 1]]
                        if not (link in seen_links):
                            seen_links.append(link)
                            link_rssi.append([RSSIs[idx]])
                        else:
                            link_idx = seen_links.index(link)
                            link_rssi[link_idx].append(RSSIs[idx])
            avg_rssi=[np.mean(rssis_per_link) for rssis_per_link in link_rssi]
            return seen_links,avg_rssi


if __name__ == '__main__':
    pass



