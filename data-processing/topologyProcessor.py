__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt

from logProcessor import LogProcessor


gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''


class TopologyLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)






if __name__ == '__main__':

    folder = gl_dump_path + 'tdma/no-interference-hopping/'
    print(os.getenv("HOME"))
    p = TopologyLogProcessor(filename=folder+'no_interference_hopping.log')



