import random
import routing.LND_routing
import routing.naive_routing
from utils.common import calculate_route_fees
from utils.visualizers import visualize_routes
from utils.graph_helpers import sample_long_route, create_sub_graph_by_node_capacity
from time import time
import numpy as np

MAX_TRIALS = 1000
AMOUNT_TO_TRANSFER = 1000000
SEED = 0


def show_shortest_path_in_sparse_graph():
    """
    This is a debug function;
    it creates a sparse, connected sub-tree of the LN and samples 2 nodes and compares the naive and LND route between
    them.
    """
    start_time = time()
    graph = create_sub_graph_by_node_capacity(k=10, highest_capacity_offset=50)
    print(f'Creating graph took {time() - start_time} secs')

    lnd_route, src, dst = sample_long_route(graph, AMOUNT_TO_TRANSFER, routing.LND_routing.get_route,
                                            min_route_length=4)
    naive_route = routing.naive_routing.get_route(graph, src, dst)

    # Analyze results
    naive_fees, naive_debug_str = calculate_route_fees(graph, naive_route, AMOUNT_TO_TRANSFER, get_debug_str=True)
    lnd_fees, lnd_debug_str = calculate_route_fees(graph, lnd_route, AMOUNT_TO_TRANSFER, get_debug_str=True)
    print(f"Fees paid for transaction of {AMOUNT_TO_TRANSFER}: msat")
    print(f"\tNaive: {np.sum(naive_fees)} msat: ", naive_debug_str)
    print(f"\tLnd: {np.sum(lnd_fees)} msat", lnd_debug_str)
    diff = abs(np.sum(lnd_fees) - np.sum(naive_fees))
    print(f"Lnd saves {diff} (~{diff / np.sum(naive_fees) * 100}%) msat")

    visualize_routes(graph, src, dst, {"naive": naive_route, "LND": lnd_route})


if __name__ == '__main__':
    random.seed(SEED)
    np.random.seed(SEED)
    show_shortest_path_in_sparse_graph()
