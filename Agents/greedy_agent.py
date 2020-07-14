import networkx as nx
from matplotlib import pyplot as plt
from helpers import create_sub_graph_by_highest_node_capacity


class greedy_investor(object):
    def __init__(self, network_enviroment, 0, max_nodes=1):
        self.network_enviroment = network_enviroment
        self.balance = 0
        self.max_nodes = max_nodes


if __name__ == '__main__':
    dump_path = 'old_dumps/LN_2020.05.05-08.00.02.json'
    graph = create_sub_graph_by_highest_node_capacity(dump_path, k=50)

    greedy_investor(graph, balance=10**4, max_nodes=1, max_edges=10)

    plt.figure()
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show(block=False)
    plt.savefig("Graph.png", format="PNG")