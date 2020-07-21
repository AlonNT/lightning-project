import random

import networkx as nx
from routing.naive_routing import get_route as get_naive_route
from routing.LND_routing import get_route as get_lnd_route
from LightningGraph.utils import create_sub_graph_by_node_capacity, visualize_routes
from time import time
from tqdm import tqdm
import numpy as np

MAX_TRIALS = 1000
AMOUNT_TO_TRANSFER = 1000
SEED=0


def show_shortest_path_in_sparse_graph(min_route_length=2):
    start_time = time()
    graph = create_sub_graph_by_node_capacity(k=40, highest_capacity_offset=50)
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

    visualize_routes(graph, src, dest, [naive_route, lnd_route])


if __name__ == '__main__':
    random.seed(SEED)
    np.random.seed(SEED)
    show_shortest_path_in_sparse_graph(min_route_length=4)
