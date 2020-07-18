import random

import networkx as nx
import matplotlib.pyplot as plt
from routing.naive_routing import get_route as get_naive_route
from routing.LND_routing import get_route as get_lnd_route
from LightningGraph.helpers import create_sub_graph_by_node_capacity
from time import time
from tqdm import tqdm

MAX_TRIALS = 1000
AMOUNT_TO_TRANSFER = 1000


def show_shortest_path_in_sparse_graph(min_route_length=2):
    start_time = time()
    graph = create_sub_graph_by_node_capacity(k=20, highest_capacity_offset=100)
    print(f'Creating graph took {time()-start_time} secs')

    # Select random two nodes as src and dest, with the route between them being of length at least 'min_route_length'.
    start_time = time()
    unisolated_nodes = list(set(graph) - set(nx.isolates(graph)))
    print("num un-isolated nodes in graph: ", len(unisolated_nodes))

    for trial in tqdm(range(MAX_TRIALS)):
        src = random.choice(unisolated_nodes)
        dest = random.choice(unisolated_nodes)

        naive_route = get_naive_route(graph, src, dest, AMOUNT_TO_TRANSFER)
        lnd_route, amount_source_needs, lnd_route_weight = get_lnd_route(graph, src, dest, AMOUNT_TO_TRANSFER)

        if (naive_route is not None) and (len(naive_route) >= min_route_length or len(lnd_route) >= min_route_length):
            break

    if trial == MAX_TRIALS - 1:
        raise RuntimeError("Error: Too hard to find route in graph. Consider changing restrictions or graph")

    print(f'Nodes and route found after {trial} trials and took {time() - start_time} secs')

    start_time = time()
    positions = nx.spring_layout(graph)
    print(f'positioning graph took {time()-start_time} secs')

    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]

    naive_route_nodes = [r[0] for r in naive_route] + [naive_route[-1][1]]
    lnd_route_nodes = [r[0] for r in lnd_route] + [lnd_route[-1][1]]

    nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')

    nx.draw_networkx_nodes(graph, positions, nodelist=naive_route_nodes,
                           node_color='r', edgecolors='k', alpha=0.5)
    nx.draw_networkx_edges(graph, positions, edgelist=naive_route,
                           edge_color='r', width=10, edgecolors='k', label='naive', alpha=0.5)

    nx.draw_networkx_nodes(graph, positions, nodelist=lnd_route_nodes,
                           node_color='g', edgecolors='g', alpha=0.5)
    nx.draw_networkx_edges(graph, positions, edgelist=lnd_route,
                           edge_color='g', width=10, edgecolors='k', label='lnd', alpha=0.5)

    plt.text(src_x, src_y, s='source', bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor='red', alpha=0.5))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    show_shortest_path_in_sparse_graph(min_route_length=4)
