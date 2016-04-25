__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt
import networkx as nx
import operator

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

    def plot_colormap(self, nodes,node_weights,links,link_weights ,axis=None):

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

        pos = nx.circular_layout(G)
        # pos=[ {x,x} for x in range(len(nodes))]
        #print(pos)

        colors = [data[2] for data in l]
        if axis is None:
            nx.draw(G, pos, node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)
        else:
            nx.draw(G, pos, ax=axis ,node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)

        return

    def plot_multi_colormap(self, nodes, node_weights, links1, link_weights1, links2, link_weights2, axis=None):

        G = nx.MultiGraph()

        # print(nodes)
        G.add_nodes_from(nodes)

        nodes_occurrences = [(node, node_weights[idx]) for idx, node in enumerate(nodes)]
        # print(nodes)
        # print(G.nodes())
        s_nodes = sorted(nodes_occurrences, key=itemgetter(0))
        # print(s_nodes)
        w_nodes = [weight[1] / 10 for weight in s_nodes]
        # print(w_nodes)

        edges1 = [(link[0], link[1], link_weights1[idx]) for idx, link in enumerate(links1)]
        G.add_weighted_edges_from(edges1, key='edges1')

        edges2 = [(link[0], link[1], link_weights2[idx]) for idx, link in enumerate(links2)]
        G.add_weighted_edges_from(edges2, key='edges2')

        # print(edges)
        l = list(G.edges_iter(data='weight'))
        # print(l)

        pos = nx.circular_layout(G)
        # pos=[ {x,x} for x in range(len(nodes))]
        # print(pos)

        colors = [data[2] for data in l]
        if axis is None:
            nx.draw(G, pos, node_color='#A0CBE2', node_size=w_nodes, edge_color=colors, width=4,
                    edge_cmap=plt.cm.Blues,with_labels=True)
        else:
            nx.draw(G, pos, ax=axis, node_color='#A0CBE2', node_size=w_nodes, edge_color=colors, width=4,
                    edge_cmap=plt.cm.Blues, with_labels=True)

        #write_dot(G, 'multi.dot')

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

