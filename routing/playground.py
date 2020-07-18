import random

import networkx as nx
import matplotlib.pyplot as plt
from routing.naive_routing import get_route as get_naive_route
from routing.LND_routing import get_route as get_lnd_route
from LightningGraph.helpers import create_sub_graph_by_node_capacity
from time import time
from tqdm  import tqdm

MAX_TRIALS=1000
AMOUNT_TO_TRANSFER=1000


def show_shortest_path_in_sparse_graph(min_route_length=2):
    start_time = time()
    graph = create_sub_graph_by_node_capacity(dump_path='../LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json', k=20, highest_capacity_offset=100)
    print(f'Creating graph took {time()-start_time} secs')

    # Select random src and dest, but do not allow them to be the same node.
    # Select them as not neighbours
    start_time = time()
    unisolated_nodes = list(set(graph) - set(nx.isolates(graph)))
    print("num un-isolated nodes in graph: ", len(unisolated_nodes))
    for trial in tqdm(range(MAX_TRIALS)):
        src = random.choice(unisolated_nodes)
        dest = random.choice(unisolated_nodes)

        route = get_naive_route(graph, src, dest, AMOUNT_TO_TRANSFER)
        route_lnd = get_lnd_route(graph, src, dest, AMOUNT_TO_TRANSFER)
        if src != dest and route is not None and (len(route) >= min_route_length or len(route_lnd) >= min_route_length):
            break
    if trial == MAX_TRIALS - 1:
        print("Error: Too hard to find route in graph. Consider changing restrictions or graph")
        exit(1)
    print(f'Nodes and route found after {trial} trials and took {time()-start_time} secs')
    # Now we know that 'src' and 'dest' are two different nodes in the graph.

    start_time = time()
    positions = nx.spring_layout(graph)
    print(f'positioning graph took {time()-start_time} secs')

    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]


    route_nodes = [r[0] for r in route] + [route[-1][1]]
    route_nodes_lnd = [r[0] for r in route_lnd] + [route_lnd[-1][1]]
    nx.draw(graph, positions, with_labels=False, font_weight='bold',node_color='k')

    nx.draw_networkx_nodes(graph, positions, nodelist=route_nodes, node_color='r', edgecolors='k',alpha=0.5)
    nx.draw_networkx_edges(graph, positions, edgelist=route, edge_color='r', width=10, edgecolors='k', label='naive',alpha=0.5)

    nx.draw_networkx_nodes(graph, positions, nodelist=route_nodes_lnd, node_color='g', edgecolors='g',alpha=0.5)
    nx.draw_networkx_edges(graph, positions, edgelist=route_lnd, edge_color='g', width=10, edgecolors='k', label='lnd',alpha=0.5)

    plt.text(src_x, src_y, s='source', bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor='red', alpha=0.5))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    show_shortest_path_in_sparse_graph(min_route_length=4)
