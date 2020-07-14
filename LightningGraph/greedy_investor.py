import networkx as nx
from matplotlib import pyplot as plt
from helpers import create_sub_graph_by_highest_node_capcity


class greedy_investor(object):
    def __init__(self, graph):
        self.graph = graph


if __name__ == '__main__':
    dump_path = 'old_dumps/LN_2020.05.05-08.00.02.json'
    graph = create_sub_graph_by_highest_node_capcity(dump_path)
    greedy_investor(graph)

    plt.figure()
    nx.draw(graph)
    plt.show(block=False)
    plt.savefig("Graph.png", format="PNG")