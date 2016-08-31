__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter

from dataprocessing.log_processor import LogProcessor



gl_dump_path = os.getcwd() + '/../shared'
gl_image_path = os.getenv("HOME") + ''


class TopologyLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def plot_sg_colormap(self, nodes,node_weights,links,link_weights ,axis=None,boolIF=None):

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
            nx.draw_networkx_edges(G, pos, edge_color=colors, width=4, edge_vmin=-2000 , edge_vmax=max(colors),
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

    def plot_sg_multi_colormap(self, nodes, node_weights, links1, link_weights1, links2, link_weights2):
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
        nx.draw_networkx_labels(IF, IF_pos, IF_labels, font_size=12)

        return

if __name__ == '__main__':
    pass
