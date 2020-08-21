from copy import deepcopy
from time import time
import numpy as np

from Agents.randomAgent import RandomInvestor
from LightningSimulator import LightningSimulator, transfer_money_in_graph
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity
from routing.LND_routing import get_route

SIMULATOR_NUM_NODES = 100
GRAPH_DENSITY_OFFSET=50
SIMULATOR_NUM_TRANSACTIONS = 100000
INITIAL_FUNDS = 10 ** 9
SIMULATOR_TRANSFERS_MAX_AMOUNT = 5*10 ** 6
LN_DEFAULT_CHANNEL_COST = 4 * 10 ** 4
REPS=5
from tqdm import tqdm


RANDOM_MATRICES = [np.random.rand(10,10) for _ in range(1000)]

def

def dummy_computation_sync(num_tasks=1000):
    results = dict()
    for i in range(len(RANDOM_MATRICES)):
        results[i] = np.random.rand(10,10).mean()

def dummy_computation_Aync():
    pass



def get_all_routes_sync(graph):
    results = dict()
    for src in tqdm(graph.nodes()):
        for dest in graph.nodes():
            if dest != src:
                results[(src, dest)] = get_route(graph, src, dest, SIMULATOR_TRANSFERS_MAX_AMOUNT)
    return results

def get_all_routes_Async(graph):
    for src in tqdm(graph.nodes()):
        for dest in graph.nodes():
            if dest != src:
                results[(src, dest)] = get_route(graph, src, dest, SIMULATOR_TRANSFERS_MAX_AMOUNT)
    results = dict()
    return results


def transfer_in_all_routes_sync(graph, routes):
    success = 0
    for key, route in routes.items():
        length = transfer_money_in_graph(graph, SIMULATOR_TRANSFERS_MAX_AMOUNT,route)
        if length == len(route):
            success += 1
    return success/float(len(routes))

def main():
    graph = create_sub_graph_by_node_capacity(dump_path="../LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json",
                                              k=SIMULATOR_NUM_NODES,
                                              highest_capacity_offset=GRAPH_DENSITY_OFFSET)
    simulator = LightningSimulator(graph, num_transactions=SIMULATOR_NUM_TRANSACTIONS,
                                   transfer_amount=SIMULATOR_TRANSFERS_MAX_AMOUNT,
                                   other_balance_proportion=1.0)

    new_node_pub_key = simulator.create_agent_node()


    agent = RandomInvestor(public_key=new_node_pub_key,
                              initial_funds=INITIAL_FUNDS,
                              channel_cost=LN_DEFAULT_CHANNEL_COST)

    new_edges = agent.get_channels(simulator.graph)


    simulator.add_edges(new_edges)

    find_routes_time = []
    use_routes_time = []
    print("Startint measuring time")
    for rep in range(REPS):
        graph_copy = deepcopy(simulator.graph)

        start = time()
        all_routes = get_all_routes_sync(graph_copy)
        find_routes_time.append(time() - start)

        start = time()

        success_rate = transfer_in_all_routes_sync(graph_copy, all_routes)
        use_routes_time.append(time() - start)
        # print(f"Sucess_rate: {success_rate:.2f}")

    find_routes_time = np.array(find_routes_time)
    use_routes_time = np.array(use_routes_time)
    print(f"Find all routes: avg ({find_routes_time.mean():.2f}), std ({find_routes_time.std():.2f})")
    print(f"Use all routes: avg ({use_routes_time.mean():.2f}), std ({use_routes_time.std():.2f})")


if __name__ == '__main__':
    main()