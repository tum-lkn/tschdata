__author__ = 'Mikhail Vilgelm'

import os, re
import ast
import seaborn
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

from logProcessor import LogProcessor
from helperFunctions import mean_confidence_interval

gl_num_active_slots = 13
gl_num_off_slots = 2
gl_num_serial_slots = 2

gl_mote_range = range(1, 14)

gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getcwd() + '/images/'

gl_save = False

class Schedule:

    def __init__(self, num_slots, num_off, num_serial, t_slot=0.015):
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

    @property
    def frame_length(self):
        return len(self.schedule)*self.t_slot

    def get_min_link_delay(self, start, end):
        """

        :param start: source mote
        :param end: destination mote
        :return: minimum delay in seconds
        """
        if start <= end:
            return (end-start)*self.t_slot
        else:
            return self.frame_length - ((start - end)*self.t_slot)

    def get_min_delay_heatmap(self):
        adj_matrix = []
        for i in range(self.num_slots):
            adj_matrix.append([self.get_min_link_delay(i+1, j+1) for j in range(self.num_slots)])

        return adj_matrix

    def plot_min_delay_heatmap(self):
        data = self.get_min_delay_heatmap()
        plt.figure()
        seaborn.heatmap(data=data, xticklabels=[i for i in gl_mote_range], yticklabels=[i for i in gl_mote_range])
        if gl_save:
            plt.savefig(gl_image_path+'t_min_heatmap.png', format='png', bbox='tight')

    def get_min_path_delay(self, path):
        '''
        Get minimum delay along the path
        :param path: list of motes
        :return:
        '''
        # return sum([self.get_min_link_delay(hop, hop+1) for idx, hop in enumerate(path) if (idx != len(path)-1)])
        delay = 0.0
        for idx, hop in enumerate(path):
            if idx == 0:
                delay += 0.0
            else:
                delay += self.get_min_link_delay(hop-1, hop)
        return delay

    def get_min_packet_delay(self, pkt):
        '''
        Get minimum delay along the path
        :param path: list of (mote, retx)
        :return:
        '''
        delay = 0.0
        for idx, hop in enumerate(pkt.hop_info):
            if idx == 0:
                # first hop - consider half delay for the first retransmission
                # delay += 0.5*self.frame_length + self.frame_length*(3 - hop['retx'])
                delay += self.frame_length*(3 - hop['retx'])
            else:
                delay += (self.get_min_link_delay(pkt.hop_info[idx-1]['addr'], hop['addr']) +
                         self.frame_length*(3 - hop['retx']))
            # else:
#                delay += (self.get_min_link_delay(hop['addr'], 1) +
#                         self.frame_length*(3 - hop['retx']))

        return delay


class DelayLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        self.schedule = kwargs.pop('schedule')
        super().__init__(**kwargs)

    def get_all_paths_w_delay(self):
        '''
        :return: a list of (path, delay) to delay array values
        '''
        seen_paths = set()
        paths_real = []
        paths_min = []

        for pkt in self.packets:
            if pkt.delay>=0:
                path = pkt.get_path()
                if not (str(path) in seen_paths):
                    paths_real.append((path, [pkt.delay]))
                    paths_min.append((path, [self.schedule.get_min_packet_delay(pkt)]))
                    seen_paths.add(str(path))
                else:
                    for idx, t in enumerate(paths_min):
                        if t[0] == path:
                            real_delay = pkt.delay
                            min_delay = self.schedule.get_min_packet_delay(pkt)
                            # debug
                            min_path_delay = self.schedule.get_min_path_delay(t[0])
                            assert (real_delay >= min_delay)
                            assert (min_delay >= min_path_delay)

                            paths_min[idx][1].append(min_delay)
                            paths_real[idx][1].append(real_delay)
                            break
            else:
                print('negative delay...')
                print(pkt)

        return paths_real, paths_min

    def get_all_paths_w_num_pkts(self):
        '''

        :return: a hashmap of path to delay array values
        '''
        seen_paths = set()
        paths = []

        for pkt in self.packets:
            path = pkt.get_path()
            if not (str(path) in seen_paths):
                paths.append([path, 1])
                seen_paths.add(str(path))
            else:
                for idx, t in enumerate(paths):
                    if t[0] == path:
                        paths[idx][1] += 1
                        break

        return paths

    def plot_links_heatmap(self):
        '''

        :return: a hashmap of path to delay array values
        '''
        links = [[0 for i in gl_mote_range] for m in gl_mote_range]

        for pkt in self.packets:
            for idx, hop in enumerate(pkt.hop_info):
                src = hop['addr']
                if idx == (len(pkt.hop_info)-1):
                    dst = 1
                else:
                    dst = pkt.hop_info[idx+1]['addr']
                links[src-1][dst-1] += 1

        plt.figure()
        seaborn.heatmap(data=links, xticklabels=[i for i in gl_mote_range], yticklabels=[i for i in gl_mote_range])

        if gl_save:
            plt.savefig(gl_image_path+re.findall(r"(.+?)\.log", self.filename.split('/')[-1])[0]+'_link_load.png',
                        format='png', bbox='tight')

    def plot_path_delay(self, normalized=True):

        paths_real, paths_min = self.get_all_paths_w_delay()

        # plot 1
        plt.figure()
        # boxplot for real values
        # plt.boxplot([p[1] for p in paths_real])

        zipped_and_sorted = [(x,y) for (x, y) in sorted(zip(paths_min, paths_real),
                             key=lambda p: self.schedule.get_min_path_delay(p[0][0]))]

        paths_min = [z[0] for z in zipped_and_sorted]
        paths_real = [z[1] for z in zipped_and_sorted]

        # sort by minimum path length
        # paths_min = sorted(paths_min, key=lambda p: self.schedule.get_min_path_delay(p[0]+[1]))

        # plot for mean values
        plt.plot(list(range(1, len(paths_real)+1)), [np.mean(p[1]) for p in paths_real],
                 's-', label='avg delay')

        # plot for average minimum packet delays
        plt.plot(list(range(1, len(paths_real)+1)), [np.mean(p[1]) for p in paths_min],
                 '^-', label='avg min packet delay', )

        # plot for minimum path delays
        min_possible_delay = [self.schedule.get_min_path_delay(p[0]) for p in paths_min]
        plt.plot(list(range(1, len(paths_real)+1)), min_possible_delay,
                 '--',
                 label='min path delay, (1 tx)')

        # plot for minimum path delays with two retx
        plt.plot(list(range(1, len(paths_real)+1)),
                 [self.schedule.get_min_path_delay(p[0])+self.schedule.frame_length*len(p[0]) for p in paths_min],
                 '--',
                 label='min path delay, (2 tx)')

        # plot for minimum path delays with three retx
        plt.plot(list(range(1, len(paths_real)+1)),
                 [self.schedule.get_min_path_delay(p[0])+2*self.schedule.frame_length*len(p[0]) for p in paths_min],
                 '--',
                 label='min path delay, (3 tx)')

        x = range(1, len([str(p[0]) for p in paths_real])+1)
        plt.xticks(x,  [str(p[0]) for p in paths_real])
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=90)


        # plt.ylim((0, 7))
        plt.ylabel('delay, s')
        plt.xlabel('path #')
        plt.legend(loc=2)

        if gl_save:
            plt.savefig(gl_image_path+re.findall(r"(.+?)\.log", self.filename.split('/')[-1])[0]+'_path_delay.png',
                        format='png', bbox='tight')

        # return data for comparison plot

        interf_delay = []
        buffer_delay = []

        for idx, p in enumerate(paths_min):  # take every path
            for i, d in enumerate(p[1]):  # take every packet's delay
                i_delay = d - self.schedule.get_min_path_delay(p[0])
                b_delay = paths_real[idx][1][i] - d
                interf_delay.append(i_delay)
                buffer_delay.append(b_delay)

        return interf_delay, buffer_delay



    def pkt_served_per_mote(self):

        motes = [0 for i in gl_mote_range]

        for pkt in self.packets:
            for hop in pkt.hop_info:
                motes[hop['addr']-1] += 1

        print(motes)
        plt.figure()
        plt.plot(gl_mote_range, motes)

    def plot_path_load(self):
        paths = self.get_all_paths_w_num_pkts()
        print(paths)
        plt.figure()
        plt.plot([p[1] for p in paths])

        x = range(1, len(paths)+1)
        plt.xticks(x,  [str(p[0]) for p in paths])
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=90)

if __name__ == '__main__':
    # gl_save = True
    sched = Schedule(num_slots=gl_num_active_slots, num_off=gl_num_off_slots, num_serial=gl_num_serial_slots)

    sched.plot_min_delay_heatmap()

    folder = gl_dump_path + 'tdma/no-interference-hopping/'

    p = DelayLogProcessor(filename=folder+'no_interference_hopping.log', schedule=sched)

    int_delay0, buf_delay0 = p.plot_path_delay()
    p.plot_links_heatmap()

    p1 = DelayLogProcessor(filename=folder+'interference_hopping.log', schedule=sched)
    int_delay1, buf_delay1 = p1.plot_path_delay()
    p1.plot_links_heatmap()

    # comparison figure for different delays
    plt.figure()

    zipped = [int_delay0, int_delay1, buf_delay0, buf_delay1]

    # print([np.mean(s) for s in zipped])
    # print([mean_confidence_interval(s) for s in zipped])

    plt.boxplot(zipped)
    plt.ylim((-0.1, 1.5))

    x = range(1, 5)
    plt.xticks(x,  ['int (no int)', 'int (int)', 'buf (no int)', 'buf (int)'])
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)

    plt.savefig(gl_image_path+'delay_sources.png',
                        format='png', bbox='tight')

    seaborn.plt.show()
    # plt.show()

