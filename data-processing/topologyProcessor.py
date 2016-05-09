__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt
import networkx as nx

from logProcessor import LogProcessor
from operator import itemgetter
from networkx.drawing.nx_agraph import write_dot
#from dataSetProcessor import DataSetProcessor


gl_dump_path = os.getcwd() + '/../shared'
gl_image_path = os.getenv("HOME") + ''


class TopologyLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def get_seen_paths(self):
    #     seen_paths = set()
    #     for pkt in self.packets:
    #         path = pkt.get_path()
    #         if not (str(path) in seen_paths):
    #             seen_paths.add(str(path))
    #
    #     return seen_paths
    #
    # def get_seen_nodes(self):
    #     seen_nodes = []
    #     node_occurrences = []
    #
    #     for pkt in self.packets:
    #         for node in pkt.get_path(full=True):
    #             if not (node in seen_nodes):
    #                 seen_nodes.append(node)
    #                 node_occurrences.append(1)
    #             else:
    #                 node_idx = seen_nodes.index(node)
    #                 node_occurrences[node_idx] += 1
    #
    #     return seen_nodes,node_occurrences
    #
    # def get_seen_links(self):
    #     seen_links = []
    #     link_occurrences = []
    #
    #     for pkt in self.packets:
    #         path=pkt.get_path(full=True)
    #         for idx,node in enumerate(path):
    #             if idx!=len(path)-1:
    #                 link=[path[idx],path[idx+1]]
    #                 if not (link in seen_links):
    #                     seen_links.append(link)
    #                     link_occurrences.append(1)
    #                 else:
    #                     link_idx=seen_links.index(link)
    #                     link_occurrences[link_idx] += 1
    #
    #     return seen_links,link_occurrences

    def plot_colormap(self, nodes,node_weights,links,link_weights ,axis=None,boolIF=None):

        G = nx.Graph()

        #print(nodes)
        G.add_nodes_from(nodes)

        nodes_occurrences= [(node, node_weights[idx]) for idx, node in enumerate(nodes)]
        # print(nodes)
        # print(G.nodes())
        s_nodes=sorted(nodes_occurrences,key=itemgetter(0))
        # print(s_nodes)
        w_nodes=[weight[1]/10 for weight in s_nodes]
        # print(w_nodes)

        edges = [(link[0], link[1], link_weights[idx]) for idx, link in enumerate(links)]
        G.add_weighted_edges_from(edges)

        #print(edges)
        l=list(G.edges_iter(data='weight'))
        #print(l)


        colors = [data[2] for data in l]

        # pos = nx.circular_layout(G)
        # pos=[ {x,x} for x in range(len(nodes))]
        # print(pos)

        # v0.3
        pos = {1: (330, 600), 2: (175, 175), 3: (300, 80), 4: (550, 175), 5: (590, 500), 6: (650, 80),
               7: (930, 175), 8: (1050, 175), 9: (65, 80), 10: (930, 80), 11: (830, 600), 12: (330, 480),
               13: (780, 80)}

        if axis is None:
            #nx.draw(G, pos, node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)
            nx.draw_networkx_edges(G, pos, alpha=0.8, edge_color=colors, width=4, edge_vmin=-20 , edge_vmax=max(colors),
                                   edge_cmap=plt.cm.Reds, with_labels=True)

            nx.draw_networkx_nodes(G, pos, node_color='#E2785D', node_size=w_nodes, with_labels=True)
        else:
            nx.draw(G, pos, ax=axis ,node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)

        labels = {}
        labels[1] = "1\nDAGroot"
        for i in range(2, 14):
            labels[i] = i
        nx.draw_networkx_labels(G, pos, labels, font_size=12)

        plt.axis('off')

        if boolIF:
            # IF Graph
            IF = nx.Graph()
            IF_nodes = [15, 16, 17, 18, 19]
            IF_edges = [(15, 16), (17, 18), (18, 19)]
            IF_pos = {15: (430, 616), 16: (430, 500), 17: (840, 220), 18: (660, 220), 19: (710, 616)}
            IF_labels = {15: "AP 1", 16: "D1", 17: " D2", 18: "AP 2", 19: "D3"}
            IF.add_nodes_from(IF_nodes)
            IF.add_edges_from(IF_edges)

            # IF Graph plots
            nx.draw_networkx_edges(IF, IF_pos, width=2)
            nx.draw_networkx_nodes(IF, IF_pos, node_color='#FFFFFF', node_size=1000,  with_labels=True)
            nx.draw_networkx_labels(IF, IF_pos, IF_labels, font_size=12)

        return

    def plot_multi_colormap(self, nodes, node_weights, links1, link_weights1, links2, link_weights2):
        """

        :param nodes:
        :param node_weights:
        :param links1: same as links2
        :param link_weights1: occurences (non-normalized)
        :param links2: same as links1
        :param link_weights2: RSSIs (non-normalized)
        :param axis:
        :return:
        """
        #IF Graph
        IF = nx.Graph()
        IF_nodes = [15,16,17,18,19]
        IF_edges = [(15,16),(17,18),(18,19)]
        IF_pos = {15: (430, 616), 16: (430, 500), 17: (840, 220), 18:(660,220) , 19: (710, 616)}
        IF_labels = {15:"AP 1",16:"UE 1",17:"AP 2",18:"UE 2",19:"UE 3"}
        IF.add_nodes_from(IF_nodes)
        IF.add_edges_from(IF_edges)

        #WSN Graph
        G = nx.Graph()

        # print(nodes)
        G.add_nodes_from(nodes)

        nodes_occurrences = [(node, node_weights[idx]) for idx, node in enumerate(nodes)]
        s_nodes = sorted(nodes_occurrences, key=itemgetter(0))
        w_nodes = [weight[1] / 10 for weight in s_nodes]

        # retrive occurences
        edges1 = [(link[0], link[1], link_weights1[idx]) for idx, link in enumerate(links1)]
        G.add_weighted_edges_from(edges1, key='edges1')
        l = list(G.edges_iter(data='weight'))
        colors = [data[2]/100 for data in l]

        # weird stuff happening... why do I write this?
        G_temp = nx.Graph()
        G_temp.add_nodes_from(nodes)
        edges1 = [(link[0], link[1], link_weights2[idx]) for idx, link in enumerate(links1)]
        G_temp.add_weighted_edges_from(edges1, key='edges1')
        l = list(G_temp.edges_iter(data='weight'))
        edgewidth = [data[2]/8 for data in l]

        #v0.1
        # pos = {1: (335, 630), 2: (220, 90), 3: (350, 90), 4: (590, 90), 5: (590, 590), 6: (710, 90),
        #        7: (840, 590), 8: (975, 590), 9: (90, 50), 10: (970, 90), 11: (710, 590), 12: (335, 530),
        #        13: (840, 90)}

        #v0.2
        # pos = {1: (330, 690), 2: (175, 175), 3: (300, 80), 4: (550, 175), 5: (590, 570), 6: (650, 80),
        #        7: (930, 175), 8: (1050, 175), 9: (65, 80), 10: (930, 80), 11: (830, 630), 12: (330, 570),
        #        13: (780, 80)}

        #v0.3
        pos = {1: (330, 600), 2: (175, 175), 3: (300, 80), 4: (550, 175), 5: (590, 500), 6: (650, 80),
               7: (930, 175), 8: (1050, 175), 9: (65, 80), 10: (930, 80), 11: (830, 600), 12: (330, 480),
               13: (780, 80)}

        # finally draw
        # width - RSSI, color intensity - occurences
        nx.draw_networkx_edges(G, pos, alpha=0.8, width=edgewidth,
                                   edge_color=colors, edge_cmap=plt.cm.Reds, edge_vmin=-50, edge_vmax=max(colors),
                                   with_labels=True)

        nx.draw_networkx_nodes(G, pos, node_color='#E2785D', node_size=w_nodes, with_labels=True)



        labels = {}
        labels[1]="1\nDAGroot"
        for i in range(2,14):
            labels[i]=i
        nx.draw_networkx_labels(G, pos, labels, font_size=12)

        plt.axis('off')

        #IF Graph plots
        nx.draw_networkx_edges(IF, IF_pos)
        #nx.draw_networkx_nodes(IF, IF_pos, node_color='#FFFFFF', with_labels=True)
        nx.draw_networkx_labels(IF, IF_pos, IF_labels, font_size=12)

        return

if __name__ == '__main__':

    folder = gl_dump_path
    #
    # p = TopologyLogProcessor(filename=folder+'/no_interference.log')
    #
    # p.plot_colormap(file_path=folder+'/no_interference.log')
    # plt.show()

    # motes,node_occurrences=p.get_seen_nodes()
    # links,link_occurrences=p.get_seen_links()
    #
    # G = nx.Graph()
    #
    # print(motes)
    # G.add_nodes_from(motes)
    #
    # nodes= [(node, node_occurrences[idx]) for idx, node in enumerate(motes)]
    # # print(nodes)
    # # print(G.nodes())
    # s_nodes=sorted(nodes,key=itemgetter(0))
    # # print(s_nodes)
    # w_nodes=[weight[1]/10 for weight in s_nodes]
    # # print(w_nodes)
    #
    # edges = [(link[0], link[1], link_occurrences[idx]) for idx, link in enumerate(links)]
    # G.add_weighted_edges_from(edges)
    #
    # #print(edges)
    # l=list(G.edges_iter(data='weight'))
    # #print(l)
    #
    #
    # pos = nx.circular_layout(G)
    # #pos=[ {x,x} for x in range(len(nodes))]
    # #print(pos)
    #
    # colors = [data[2] for data in l]
    #
    # # create subplots
    # f, axs = plt.subplots(2, sharex=True)
    #
    # # pass the axis as a parameter
    # nx.draw(G, pos, ax=axs[0], node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)
    #
    # nx.draw(G, pos, ax=axs[1], node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)
    #
    # plt.savefig("images/edge_colormap.png")  # save as png
    # plt.show()  # display

