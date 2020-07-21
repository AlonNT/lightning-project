import random
from routing.LND_routing import get_route as get_lnd_route
from utils.common import calculate_route_fees
from utils.visualizers import visualize_routes
from utils.graph_helpers import sample_long_route, create_sub_graph_by_node_capacity
from time import time
import numpy as np

MAX_TRIALS = 1000
AMOUNT_TO_TRANSFER = 1000000
SEED=0


def show_shortest_path_in_sparse_graph(min_route_length=2):
    start_time = time()
    graph = create_sub_graph_by_node_capacity(k=40, highest_capacity_offset=50)
    print(f'Creating graph took {time()-start_time} secs')

    sample_long_route(graph, AMOUNT_TO_TRANSFER, get_lnd_route, min_route_length=4)

    ## Analyze resuts
    naive_fees = calculate_route_fees(graph, naive_route, AMOUNT_TO_TRANSFER)
    lnd_fees = calculate_route_fees(graph, lnd_route, AMOUNT_TO_TRANSFER)
    print(f"Fees paid for transaction of {AMOUNT_TO_TRANSFER}: msat")
    print(f"\tNaive: {np.sum(naive_fees)} msat")
    print(f"\tLnd: {np.sum(lnd_fees)} msat")
    diff = abs(np.sum(lnd_fees) - np.sum(naive_fees))
    print(f"Lnd saves {diff} (~{int(diff/np.sum(naive_fees)*100)}%) msat")


    visualize_routes(graph, src, dest, [naive_route, lnd_route])


if __name__ == '__main__':
    random.seed(SEED)
    np.random.seed(SEED)
    show_shortest_path_in_sparse_graph(min_route_length=4)
