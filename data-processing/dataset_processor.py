__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt
import networkx as nx
import operator
import numpy
from scipy.misc import imread
import matplotlib.cbook as cbook

from log_processor import LogProcessor
from operator import itemgetter
from topology_processor import TopologyLogProcessor

gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''


class DataSetProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == '__main__':

# # Smartgrid Data processing
#
#
#     folders= ('tdma','shared')
#     files= ('1-1-no_interference','2-1-interference','3-1-induced_interference','4-1-high_load')
#     #files= ('no_interference','interference','induced_interference','high_load')
#
#     tot_packets=[]
#     duration=[]
#     tot_per_node_packets=[]
#     tot_per_channel_packets = []
#
#     # create subplots
#     # f, axs = plt.subplots(2,3)
#     # f.subplots_adjust(hspace=0)
#
#     k=1;
#     for i,folder in enumerate(folders):
#         for j,file in enumerate(files):
#
#             path = gl_dump_path + folder + '/' + file + '.log'
#             print(path)
#
#             d = DataSetProcessor(filename=path)
#
#             tp=d.get_total_packets()
#             dur = d.get_total_duration() / 60  # in minutes
#             nodes_occurrences=d.get_seen_nodes()
#             channels_occurrences=d.get_seen_channels()
#             links,link_occurrences=d.get_seen_links()
#             links, link_rssis = d.get_seen_links(type="RSSI")
#
#
#             print("\n")
#             print(folder+'-'+file)
#
#             print("Total duration [min]:\n", dur)
#             print("Total number of packets:\n", tp)
#
#             #print("Nodes occurrences:\n",nodes_occurrences)
#             #print("Channels occurrences:\n", channels_occurrences)
#             tot_avg_node_occurr = numpy.mean(list(nodes_occurrences.values()))
#             tot_avg_channel_occurr = numpy.mean(list(channels_occurrences.values()))
#
#             print("Nodes occurrences (avg):\n", tot_avg_node_occurr)
#             print("Channels occurrences (avg):\n", tot_avg_channel_occurr)
#
#             tot_packets.append(tp)
#             duration.append(dur)
#             tot_per_channel_packets.append(tot_avg_channel_occurr)
#             tot_per_node_packets.append(tot_avg_node_occurr)
#
#             p = TopologyLogProcessor(filename=path)
#
#
#             #plt.figure(figsize=(15, 4))
#             fig=plt.figure()
#             # if folder is 'tdma':
#             #     fig.suptitle(folder.upper() + '-' + file)
#             # else:
#             #     fig.suptitle(folder.title() + '-' + file)
#
#             datafile = cbook.get_sample_data(os.getcwd()+"/images/LKN_plan_v0.3.jpg")
#
#             #ax=plt.subplot(2,3,k)
#             #ax.set_title((folder+'-'+file).title())
#             k += 1
#             img = imread(datafile)
#             plt.imshow(img)#, zorder=0, extent=[0, 24.0, -1, 2.0])
#
#             if j is 2:
#                 p.plot_sg_colormap(nodes=list(nodes_occurrences.keys()),node_weights=list(nodes_occurrences.values())
#                             ,links=links,link_weights=link_occurrences,boolIF=True)
#             else:
#                 p.plot_sg_colormap(nodes=list(nodes_occurrences.keys()), node_weights=list(nodes_occurrences.values())
#                             , links=links, link_weights=link_occurrences, boolIF=False)
#
#             # p.plot_sg_multi_colormap(nodes=list(nodes_occurrences.keys()),
#             #                       node_weights=list(nodes_occurrences.values()),links1=links,
#             #                      link_weights1=link_occurrences,links2=links,link_weights2=link_rssis)
#             plt.tight_layout()
#             plt.savefig("images/topology_colormap_"+folder+'_'+file+"FINAL.pdf", format='pdf')
#
#             #break
#         #break
#
#     print(duration)
#     print(tot_per_node_packets)
#     print(tot_per_channel_packets)
#     print(tot_packets)
#
#     # plt.tight_layout()
#     # plt.savefig("images/all_topologies_colormap.png")
#     plt.show()

# Whitening Data processing
    tot_packets=[]
    duration=[]
    tot_per_node_packets=[]
    tot_per_channel_packets = []

    for i in range(1, 3):
        print("\n")

        d = DataSetProcessor(filename="../../WHData/Data/LKN_measurements_140716/Logs/%d.log" % i,
                   format="WHITENING")

        tp=d.get_total_packets()
        dur = d.get_total_duration() / 60  # in minutes
        nodes_occurrences=d.get_seen_nodes()
        channels_occurrences=d.get_seen_channels()
        links,link_occurrences=d.get_seen_links()
        links, link_rssis = d.get_seen_links(type="RSSI")

        print("File log: %d.log" % i)
        print("Total duration [min]:\n", dur)
        print("Total number of packets:\n", tp)

        #print("Nodes occurrences:\n",nodes_occurrences)
        #print("Channels occurrences:\n", channels_occurrences)
        tot_avg_node_occurr = numpy.mean(list(nodes_occurrences.values()))
        tot_avg_channel_occurr = numpy.mean(list(channels_occurrences.values()))

        print("Nodes occurrences (avg):\n", tot_avg_node_occurr)
        print("Channels occurrences (avg):\n", tot_avg_channel_occurr)

        tot_packets.append(tp)
        duration.append(dur)
        tot_per_channel_packets.append(tot_avg_channel_occurr)
        tot_per_node_packets.append(tot_avg_node_occurr)

    print("\n")
    print(duration)
    print(tot_per_node_packets)
    print(tot_per_channel_packets)
    print(tot_packets)