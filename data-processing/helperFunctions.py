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

gl_t_slot = 0.015  # in seconds

class TestbedPacket:

    @classmethod
    def serialize_data(cls, data, format='SMARTGRID'):
        """
        Factory method
        """
        if format == 'SMARTGRID':
            data = ast.literal_eval(data)
            return MeasurementPacket(asn_first=data[6:11], asn_last=data[1:6],
                                     src_addr=int(data[0]), seqN=data[11:13],
                                     hop_info=data[14:])
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

    def get_path(self):
        path = [hop['addr'] for hop in self.hop_info]
        return path

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

        pkt = TestbedPacket.serialize_data(test_pkt)

        pkt_serialized = pkt.dump_compressed()

        pkt_recovered = pickle.loads(pkt_serialized.replace(b'\\n', b'\n'))

        self.assertEqual(pkt_recovered.seqN, 234)
        self.assertEqual(pkt_recovered.src_addr, 2)


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





