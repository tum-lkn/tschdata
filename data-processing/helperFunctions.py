"""
Helper functions and basic data structures for processing of logged packet.
"""
__author__ = 'Mikhail Vilgelm'

import pickle
import pprint
import unittest
import numpy as np
import ast
import os
import math
import scipy.stats as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

gl_t_slot = 0.015  # in seconds

gl_hopping_sequence = [5,9,12,7,15,4,14,11,8,0,1,2,13,3,6,10]
gl_hopping_sequence = [f+11 for f in gl_hopping_sequence]

class TestbedPacket:

    @classmethod
    def load_data(cls, data, timestamp, format='SMARTGRID'):
        """
        Factory method
        """
        if format == 'SMARTGRID':
            data = ast.literal_eval(data)
            return MeasurementPacket(asn_first=data[6:11], asn_last=data[1:6],
                                     src_addr=int(data[0]), seqN=data[11:13],
                                     hop_info=data[14:], timestamp=timestamp)
        elif format == 'AIRCRAFT':
            return StringPacket(data)


class StringPacket(TestbedPacket):
    """
    Packets sniffed from aircraft measurments
    """

    def __init__(self, data):
        self.data = data


    def dump_compressed(self):
        return self.data



class MeasurementPacket(TestbedPacket):
    """
    Packet sniffed for smartgrid measurements
    asn_first, asn_last, seqN - integers
    hop_info - list, where every entry is a dictionary
    """

    def __init__(self, **kwargs):
        """
        Instantiate a measurements packet object
        :param
        :return:
        """
        if 'timestamp' in kwargs.keys():
            self.timestamp = kwargs['timestamp']
        # print(kwargs['asn_first'])
        self.asn_first = self.list_to_int(kwargs['asn_first'])
        # print(self.asn_first)
        self.asn_last = self.list_to_int(kwargs['asn_last'])

        self.seqN = self.list_to_int(kwargs['seqN'])
        num_hops = int(len(kwargs['hop_info'])/4)  # assume 4 bytes per hop entry
        self.hop_info = []
        for i in [4*x for x in range(num_hops)]:
            hop_info_temp = {'addr': int(kwargs['hop_info'][i]),
                                  'retx': int(kwargs['hop_info'][i+1]),
                                  'freq': int(kwargs['hop_info'][i+2]),
                                  'rssi': int(kwargs['hop_info'][i+3])}
            if hop_info_temp['addr'] != 0:
                self.hop_info.append(hop_info_temp)

        self.src_addr = self.hop_info[0]['addr']

    def dump_as_ipv6(self):
        """
        Recover full ipv6 packet from a compressed entry
        :return:
        """
        # TODO
        # recover ipv6 header
        # recover udp header
        pass

    def dump_compressed(self):
        """
        Serialize object and return as bytes + escape the newline character
        :return:
        """
        dump = pickle.dumps(self)
        return dump.replace(b'\n', b'\\n')

    def serialize(self):
        """
        Serialize object and return as bytes + escape the newline character
        :return:
        """
        dump = self.__dict__
        return dump

    def list_to_int(self, l):
        """
        Convert a multibyte value to a single number
        :param l:
        :return:
        """
        temp = [(256**idx)*int(x) for idx, x in enumerate(l)]
        temp[0] = l[0]
        return sum(temp)

    @property
    def delay(self):
        return (self.asn_last - self.asn_first)*gl_t_slot

    def num_hops(self):
        num_hops = 0
        for hop in self.hop_info:
            if hop['addr'] != 0:
                num_hops += 1
        return num_hops

    def get_path(self, full=True):
        path = [hop['addr'] for hop in self.hop_info]
        if full:
            return path + [1]
        else:
            return path
    
    def get_channels(self):
        channels = [hop['freq'] for hop in self.hop_info]
        return channels

    def get_first_hop_waiting_time(self):
        first_hop_info = self.hop_info[-1]
        assert (first_hop_info['addr'] != 0)
        ch = first_hop_info['freq']
        asn_tx = gl_hopping_sequence.index(ch)-1
        time = asn_tx - (self.asn_first % 16)
        if time >= 0:
            return time
        else:
            return 17 - (self.asn_first % 16) + asn_tx

    def get_rssi(self):
        RSSIs = [hop['rssi'] for hop in self.hop_info]
        return RSSIs

class TestTestbedPackets(unittest.TestCase):
    """
    Unit tests
    """

    def test_recovering(self):
        """
        Test whether serializing and recovering works
        :return:
        """
        test_pkt = '[2, 1, 65, 1, 0, 0, 239, 64, 1, 0, 0, 234, 0, 0, 2, 3, 23, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]'

        pkt = TestbedPacket.load_data(test_pkt)

        pkt_serialized = pkt.dump_compressed()

        pkt_recovered = pickle.loads(pkt_serialized.replace(b'\\n', b'\n'))

        self.assertEqual(pkt_recovered.seqN, 234)
        self.assertEqual(pkt_recovered.src_addr, 2)

    def test_serialization(self):
        test_pkt = '[2, 1, 65, 1, 0, 0, 239, 64, 1, 0, 0, 234, 0, 0, 2, 3, 23, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]'
        pkt = TestbedPacket.load_data(test_pkt)
        print(pkt.serialize())


def find_latest_dump(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))[-1]


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), st.sem(a)
    h = se * st.t._ppf((1+confidence)/2., n-1)
    return h


if __name__ == '__main__':
    '''
    Testing
    '''
    unittest.main()





