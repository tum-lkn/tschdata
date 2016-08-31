"""
Helper functions and basic data structures for processing of logged packet.
"""

import scipy.stats as st
from pylab import setp
import os
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import json


class Schedule:

    def __init__(self, num_slots, num_off, num_serial, s_active_slots=None, hopping_seq=None, m_slot_map=None, t_slot=0.015, shared=False):
        """
        Assumption: every active slot corresponds to a mote with addr = slot#
        :param num_slots: number of active slots
        :param num_off: number of OFF slots
        :param num_serial: number of serial slots
        :param t_slot: slot duration in ms
        :return:
        """
        self.num_slots = num_slots
        self.num_off = num_off
        self.num_serial = num_serial
        self.schedule = [i for i in range(1, num_slots+1)]
        self.schedule += [0 for i in range(num_off+num_serial)]
        self.t_slot = t_slot  # in s

        if not (hopping_seq is None):
            self.hopping_sequence = hopping_seq

        if not (m_slot_map is None):
            self.mote_slot_map = m_slot_map

        if not (s_active_slots is None):
            self.active_slots = s_active_slots

        self.shared = shared

    @property
    def frame_duration(self):
        return len(self.schedule)*self.t_slot

    @property
    def frame_length(self):
        return len(self.schedule)

    def get_min_link_delay(self, start, end):
        """

        :param start: source mote
        :param end: destination mote
        :return: minimum delay in seconds
        """
        if start <= end:
            return (end-start)*self.t_slot
        else:
            return self.frame_duration - ((start - end) * self.t_slot)

    def get_min_delay_heatmap(self):
        """
        Get data to plot minimum (link) delay heatmap for every link (TDMA)
        :return:
        """
        adj_matrix = []
        for i in range(self.num_slots):
            adj_matrix.append([self.get_min_link_delay(i+1, j+1) for j in range(self.num_slots)])

        return adj_matrix

    def plot_min_delay_heatmap(self):
        """
        Plot minimum link delays for the topology
        :return:
        """
        data = self.get_min_delay_heatmap()
        plt.figure()
        heatmap(data=data, xticklabels=[i for i in gl_mote_range], yticklabels=[i for i in gl_mote_range])
        if gl_save:
            plt.savefig(gl_image_path+'t_min_heatmap.png', format='png', bbox='tight')

    def get_min_path_delay(self, path):
        '''
        Get minimum delay along the path
        :param path: list of motes
        :return:
        '''
        delay = 0.0
        if not self.shared:
            # return sum([self.get_min_link_delay(hop, hop+1) for idx, hop in enumerate(path) if (idx != len(path)-1)])
            for idx, hop in enumerate(path):
                if idx == 0:
                    # consider first hop as half a frame-length
                    delay += 0.5*self.frame_duration
                    # delay += 0.0
                else:
                    delay += self.get_min_link_delay(hop-1, hop)
        else:
            delay += (len(path)-1)*self.t_slot

        return delay

    def get_min_packet_delay(self, pkt):
        '''
        Get minimum delay along the path
        :param path: list of (mote, retx)
        :return:
        '''
        delay = 0.0
        if not self.shared:
            for idx, hop in enumerate(pkt.hop_info):
                if idx == 0:
                    # first hop - consider half delay for the first retransmission
                    delay += 0.5*self.frame_duration + self.frame_duration * (3 - hop['retx'])
                else:
                    delay += (self.get_min_link_delay(pkt.hop_info[idx-1]['addr'], hop['addr']) +
                              self.frame_duration * (3 - hop['retx']))
        else:
            for idx, hop in enumerate(pkt.hop_info):
                if idx == 0:
                    delay += self.t_slot*sum([(2**i)/2 for i in range(1, 5 - hop['retx']) if i!=1])
                else:
                    delay += self.t_slot*sum([(2**i)/2 for i in range(1, 5 - hop['retx'])])
            # pass
        return delay


def find_latest_dump(path):
    """
    Find the lastest file in the folder
    :param path:
    :return:
    """
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))[-1]


def set_box_plot(bp):
    """
    Set parameters of the given boxplot
    :param bp:
    :return:
    """
    for b in bp['boxes']:
        setp(b, color='blue', linewidth=1.5)
    for c in bp['caps']:
        setp(c, color='black', linewidth=1.5)
    for w in bp['whiskers']:
        setp(w, color='blue', linewidth=1.5)
    for m in bp['medians']:
        setp(m, color='red', linewidth=1.5)
    for o in bp['fliers']:
        setp(o, markersize=8, markeredgewidth=1.5)


def set_box_plot_diff(bp):
    for idx, b in enumerate(bp['boxes']):
        if idx%2 == 1:
            setp(b, color='blue', linewidth=1.5)
        else:
            setp(b, color='red', linewidth=1.5)

    for idx, c in enumerate(bp['caps']):
        setp(c, color='black', linewidth=1.5)

    for idx, w in enumerate(bp['whiskers']):
        if idx % 2 == 1:
            setp(w, color='blue', linewidth=1.5)
        else:
            setp(w, color='red', linewidth=1.5)
    for idx, m in enumerate(bp['medians']):
        # if idx%2 == 1:
        setp(m, color='red', linewidth=1.5)


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), st.sem(a)
    h = se * st.t._ppf((1+confidence)/2., n-1)
    return h


def get_all_files(path, folders=None):
    """
    Get all files in the folder
    :param path:
    :param folders:
    :return:
    """

    files = []

    if folders is None:
        folders = [path + 'tdma/', path + 'shared/']
    else:
        folders = [path + folder + '/' for folder in folders]

    for folder in folders:
        temp = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        temp = sorted(temp)
        files += [folder+f for f in temp]

    return files


def set_figure_parameters():
    rcParams.update(
        {'figure.autolayout': True, 'font.size': 14, 'font.family': 'serif', 'font.sans-serif': ['Helvetica']})


def load_config(fname):
    config = json.load(open(fname, "r"))
    print("########### Loaded configuration file: ")
    print(config)
    print("########### End of configuration file ")

    gl_image_path = config["data_path"]
    gl_dump_path = config["image_path"]


if __name__ == '__main__':
    '''
    Testing
    '''
    pass





