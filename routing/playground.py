import random

import networkx as nx
import matplotlib.pyplot as plt
from routing.route_selection import get_route
from LightningGraph.helpers import create_sub_graph_by_highest_node_capacity


def main():
    graph = create_sub_graph_by_highest_node_capacity(k=8)

    # Select random src and dest, but do not allow them to be the same node.
    src = None
    dest = None
    while src == dest:
        src = random.choice(list(graph.nodes))
        dest = random.choice(list(graph.nodes))
    # Now we know that 'src' and 'dest' are two different nodes in the graph.

    route = get_route(graph, src, dest)
    print(route)

    positions = nx.spring_layout(graph)
    # labels = {node: node[-2:] for node in graph.nodes}

    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]

    nx.draw(graph, with_labels=False, font_weight='bold')

    plt.text(src_x, src_y,
             s='source',
             bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y,
             s='target',
             bbox=dict(facecolor='red', alpha=0.5))
    plt.show()


if __name__ == '__main__':
    main()
