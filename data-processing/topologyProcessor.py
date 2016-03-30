__author__ = 'Samuele Zoppi'

import os
import matplotlib.pyplot as plt
import networkx as nx
import operator

from logProcessor import LogProcessor
from operator import itemgetter


gl_dump_path = os.getcwd() + '/../'
gl_image_path = os.getenv("HOME") + ''


class TopologyLogProcessor(LogProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_seen_paths(self):
        seen_paths = set()
        for pkt in self.packets:
            path = pkt.get_path()
            if not (str(path) in seen_paths):
                seen_paths.add(str(path))

        return seen_paths

    def get_seen_nodes(self):
        seen_nodes = []
        node_occurrences = []

        for pkt in self.packets:
            for node in pkt.get_path(full=True):
                if not (node in seen_nodes):
                    seen_nodes.append(node)
                    node_occurrences.append(1)
                else:
                    node_idx = seen_nodes.index(node)
                    node_occurrences[node_idx] += 1

        return seen_nodes,node_occurrences

    def get_seen_links(self):
        seen_links = []
        link_occurrences = []

        for pkt in self.packets:
            path=pkt.get_path(full=True)
            for idx,node in enumerate(path):
                if idx!=len(path)-1:
                    link=[path[idx],path[idx+1]]
                    if not (link in seen_links):
                        seen_links.append(link)
                        link_occurrences.append(1)
                    else:
                        link_idx=seen_links.index(link)
                        link_occurrences[link_idx] += 1

        return seen_links,link_occurrences

if __name__ == '__main__':

    folder = gl_dump_path + 'tdma/no-interference-hopping/'

    p = TopologyLogProcessor(filename=folder+'no_interference_hopping.log')

    motes,node_occurrences=p.get_seen_nodes()
    links,link_occurrences=p.get_seen_links()

    G = nx.Graph()

    print(motes)
    G.add_nodes_from(motes)

    nodes= [(node, node_occurrences[idx]) for idx, node in enumerate(motes)]
    # print(nodes)
    # print(G.nodes())
    s_nodes=sorted(nodes,key=itemgetter(0))
    # print(s_nodes)
    w_nodes=[weight[1]/10 for weight in s_nodes]
    # print(w_nodes)

    edges = [(link[0], link[1], link_occurrences[idx]) for idx, link in enumerate(links)]
    G.add_weighted_edges_from(edges)

    #print(edges)
    l=list(G.edges_iter(data='weight'))
    #print(l)


    pos = nx.circular_layout(G)
    #pos=[ {x,x} for x in range(len(nodes))]
    #print(pos)

    colors = [data[2] for data in l]
    nx.draw(G,pos, node_color='#A0CBE2', node_size=w_nodes ,edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True)
    plt.savefig("images/edge_colormap.png")  # save as png
    plt.show()  # display

