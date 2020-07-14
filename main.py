import networkx as nx
from matplotlib import pyplot as plt
from LightningGraph.helpers import create_sub_graph_by_highest_node_capacity
from Agents.random_agent import random_investor
from Enviroments import Enviroment


def main():
    graph = create_sub_graph_by_highest_node_capacity(k=50)

    # network_enviroment = Enviroment(graph)

    random_investor(graph, balance=10**4, max_nodes=1, max_edges=10)

    plt.figure()
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show(block=False)
    plt.savefig("Graph.png", format="PNG")


if __name__ == '__main__':
    main()
