__author__ = 'Mikhail Vilgelm'

import os
import ast
import seaborn
import numpy as np
import matplotlib.pyplot as plt

from logProcessor import LogProcessor

gl_num_active_slots = 14
gl_num_off_slots = 2
gl_num_serial_slots = 2

gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''

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
        :return: minimum delay in ms
        """
        if start <= end:
            return (end-start)*self.t_slot
        else:
            return self.frame_length - (end-start)*self.t_slot

    def get_min_delay_heatmap(self):
        adj_matrix = []
        for i in range(self.num_slots):
            adj_matrix.append([self.get_min_link_delay(i+1, j+1) for j in range(self.num_slots)])

        return adj_matrix

    def plot_min_delay_heatmap(self):
        data = self.get_min_delay_heatmap()
        seaborn.heatmap(data)

    def get_min_path_delay(self, path):
        '''
        Get minimum delay along the path
        :param path: list of motes
        :return:
        '''
        return sum([self.get_min_link_delay(hop, hop+1) for idx, hop in enumerate(path) if (idx != len(path)-1)])


class DelayLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        self.schedule = kwargs.pop('schedule')
        super().__init__(**kwargs)

    def get_all_paths(self):
        '''

        :return: a hashmap of path to delay array values
        '''
        paths = dict()
        for pkt in self.packets:
            path = pkt.get_path()
            if not (str(path) in paths.keys()):
                paths[str(path)] = [pkt.delay*0.015]
            else:
                paths[str(path)].append(pkt.delay*0.015)

        # convert to list of tuples...
        return [(ast.literal_eval(key), value) for key, value in paths.items()]

    def plot_path_delay(self, normalized=True):

        paths = self.get_all_paths()

        # plt.figure()
        for p in paths:
            print(p[0])

        paths = sorted(paths, key=lambda p: np.mean(p[1]))

        plt.figure()

        set1 = [p[1] for p in paths]

        print(len(set1))

        plt.boxplot([p[1] for p in paths])

        set2 = [np.mean(p[1]) for p in paths]

        print(len(set2))

        plt.plot(list(range(1, 23)), [np.mean(p[1]) for p in paths], label='mean delay')

        path_min_delays = [self.schedule.get_min_path_delay(p[0]+[1]) for p in paths]

        plt.plot(list(range(1, 23)), path_min_delays, label='minimum delay')

        x = range(1, len([str(p[0]) for p in paths])+1)
        plt.xticks(x,  [str(p[0]) for p in paths])
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=90)


        plt.ylim((0, 2))
        plt.ylabel('delay, s')
        plt.xlabel('path #')
        plt.legend(loc=2)





if __name__ == '__main__':
    sched = Schedule(gl_num_active_slots, gl_num_off_slots, gl_num_serial_slots)

    # sched.plot_min_delay_heatmap()

    folder = gl_dump_path + 'tdma/no-interference-hopping/'

    p = DelayLogProcessor(filename=folder+'no_interference_hopping.log', schedule=sched)

    p.plot_path_delay()

    seaborn.plt.show()
    plt.show()

