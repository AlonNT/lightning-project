from garbage.SaartReproduce.routing_implementations import lnd_weight
from garbage.SaartReproduce.create_graph import load_from_disk
from tqdm import tqdm
CHUNK_SIZE=100
TRANSACTION_SIZE = 10000
NUM_OF_PROCESSES = 6
MAX_MONGO_INT = 2 ** 63 - 1
C_REPETITIONS = 4
ECLAIR_ROUTES = 3
MAX_HOPS = 15

from garbage.SaartReproduce.dijkstra import find_route

def calculate_all_best_routes(nodes_dict):
    # Multiprocessing disabled for simplicity
    nodes_list = list(nodes_dict.values())
    all_best_paths_in_graph = []
    for node in tqdm(nodes_list):
        lnd_accessible_nodes = find_route(nodes_list, target=node, get_weight=lnd_weight, msat=TRANSACTION_SIZE, max_hops=MAX_HOPS)
        for src in lnd_accessible_nodes:
            if len(lnd_accessible_nodes[src]) > 0:
                path, total, weight = lnd_accessible_nodes[src][0]  # get only first path if there is multiple
                all_best_paths_in_graph += [(path, total, weight)]

    return all_best_paths_in_graph

if __name__ == '__main__':
    nodes_dict = load_from_disk('../LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json')
    all_best_paths_in_graph = calculate_all_best_routes(nodes_dict)
