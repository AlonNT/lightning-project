from collections import defaultdict
from copy import deepcopy
from time import time
from typing import Optional

import numpy as np

from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from Agents.greedy_agent import GreedyNodeInvestor
from Agents.random_agent import RandomInvestor
from LigtningSimulator.LightningSimulator import LightningSimulator
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity

MAX_AGENT_FUNDS = 1000000
NUM_TRANSACTIONS = 100
REPEAT_SIMULATION = 10
ENVIRONMENT_NUM_NODES = 500
ENVIRONMENT_DENSITY = 100
ENVIRONMENT_TRANSFERS_MAX_AMOUNT = 10 ** 6
SIMULATION_OUT_DIR = "TRAIN_DIR"

# The channel creation cost (which is the cost payed for the bitcoin miners
# to include the channel's creation transaction in their block).
# This value changes constantly (due to the dynamics of the bitcoin transactions' fees
# that change according to the load on the blockchain).
# This approximate value was calculated using buybitcoinworldwide.com to get the cost
# of a transaction (in usd), then converting us dollars to satoshis (in 8.8.2020).
CHANNEL_CREATION_COST = 40000


def get_simulator():
    graph = create_sub_graph_by_node_capacity(k=ENVIRONMENT_NUM_NODES,
                                              highest_capacity_offset=ENVIRONMENT_DENSITY)
    simulator = LightningSimulator(graph, num_transfers=NUM_TRANSACTIONS,
                                   transfer_max_amount=ENVIRONMENT_TRANSFERS_MAX_AMOUNT)
    return simulator


def run_experiment(agent_constructors, out_dir: Optional[str] = None):
    """
    1. Creates a common Lightning environment
    for each agent:
    2. Ask agent for edges he want to establish given a funds constraint
    3. Add edges to a copy of the ENVIRONMENT
    4. Repeat simulation of so many transaction and average final balance
    param: agent_constructors: list of tuples of an agent constructor and additional Kwargs
    """
    # Create the base ENVIRONMENT whos copies will run all simulations
    env = get_simulator()
    new_node_pub_key = env.create_agent_node()

    results = defaultdict(list)
    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class heriting AbstractAgent
        agent = agent_constructor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS, **kwargs)

        print("Agent:", agent.name)
        for repeat in range(REPEAT_SIMULATION):
            env = deepcopy(env)

            # Ask agent for edges to add
            new_edges = agent.get_channels(env.get_graph())  # state is just the graph

            # Add edges to a local copy of the environment
            for edge in new_edges:
                env.add_edge(**edge)

            start = time()
            env.run()  # peforms NUM_TRANSACTIONS transactions
            print(f"\t{repeat} {human_format(NUM_TRANSACTIONS/(time()-start))} tnx/sec")

            # report revenue
            agent_balance = env.get_node_balance(new_node_pub_key) - MAX_AGENT_FUNDS
            results[agent.name] += [agent_balance]

    print(f"Score over {REPEAT_SIMULATION} simulations of {NUM_TRANSACTIONS} transactions")
    for agent_name in results:
        print(
            f"{agent_name}: mean: {human_format(np.mean(results[agent_name]))}, std: {np.mean(np.std(results[agent_name]))}")


if __name__ == '__main__':
    args = [(RandomInvestor, {}), (GreedyNodeInvestor, {}), (LightningPlusPlusAgent, {'alpha': 2})]
    run_experiment(args, out_dir=SIMULATION_OUT_DIR)
