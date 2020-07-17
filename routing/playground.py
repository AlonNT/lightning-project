import random

import networkx as nx
import matplotlib.pyplot as plt
from routing.route_selection import get_route
from LightningGraph.helpers import create_sub_graph_by_highest_node_capacity
from time import time

def main():
    start_time = time()
    graph = create_sub_graph_by_highest_node_capacity(dump_path='../LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json', k=30)
    print(f'Creating graph took {time()-start_time} secs')

    # Select random src and dest, but do not allow them to be the same node.
    # Select them as not neighbours
    trials = 0
    start_time = time()
    src = None
    dest = None
    while src == dest or dest in graph.neighbors(src):
        src = random.choice(list(graph.nodes))
        dest = random.choice(list(graph.nodes))
        trials += 1
    route = get_route(graph, src, dest)
    print(f'Nodes and route found after {trials} trials and took {time()-start_time} secs')
    # Now we know that 'src' and 'dest' are two different nodes in the graph.

    start_time = time()
    positions = nx.spring_layout(graph)
    print(f'positioning graoh took {time()-start_time} secs')

    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]


    route_nodes = [r[0] for r in route] + [route[-1][1]]
    nx.draw(graph, positions, with_labels=False, font_weight='bold',node_color='k')

    nx.draw_networkx_nodes(graph, positions, nodelist=route_nodes, node_color='r', edgecolors='k')
    nx.draw_networkx_edges(graph, positions, edgelist=route, edge_color='r', width=10, edgecolors='k')


    plt.text(src_x, src_y, s='source', bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor='red', alpha=0.5))
    plt.show()


if __name__ == '__main__':
    main()
