from collections import defaultdict
from copy import deepcopy
from time import time
from typing import Optional
import os
import numpy as np

from Agents.greedy_agent import GreedyNodeInvestor
from Agents.random_agent import RandomInvestor
from LightningSimulator import LightningSimulator
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity
import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd

MAX_AGENT_FUNDS = 10**6
ENVIRONMENT_TRANSFERS_MAX_AMOUNT = 10 ** 2
NUM_TRANSACTIONS = 1000
REPEAT_SIMULATION = 3
ENVIRONMENT_NUM_NODES = 50
ENVIRONMENT_DENSITY = 100
DEFAULT_INITIAL_FUNDS = 1000
SIMULATION_OUT_DIR = None
# The channel creation cost (which is the cost payed for the bitcoin miners
# to include the channel's creation transaction in their block).
# This value changes constantly (due to the dynamics of the bitcoin transactions' fees
# that change according to the load on the blockchain).
# This approximate value was calculated using buybitcoinworldwide.com to get the cost
# of a transaction (in usd), then converting us dollars to satoshis (in 8.8.2020).
LN_DEFAULT_CHANNEL_COST = 4*10**4

def get_simulator():
    graph = create_sub_graph_by_node_capacity(k=ENVIRONMENT_NUM_NODES,
                                              highest_capacity_offset=ENVIRONMENT_DENSITY)
    simulator = LightningSimulator(graph, num_transfers=NUM_TRANSACTIONS,
                                   transfer_max_amount=ENVIRONMENT_TRANSFERS_MAX_AMOUNT)
    return simulator


def run_experiment(agent_constructors, out_dir=None):
    """
    1. Creates a common Lightning simulator
    for each agent:
    2. Ask agent for edges it wants to establish given a funds constraint
    3. Add edges to a copy of the ENVIRONMENT
    4. Repeat simulation of so many transaction and plot average results
    param: agent_constructors: list of tuples of an agent constructor and additional Kwargs
    param: out_dir: optional directory for plotting debug images of the simulation, off if None
    """
    # Create the base ENVIRONMENT whos copies will run all simulations
    simulator = get_simulator()
    new_node_pub_key = simulator.create_agent_node()

    results = defaultdict(list)
    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class heriting AbstractAgent
        agent = agent_constructor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS,
                                  channel_cost=LN_DEFAULT_CHANNEL_COST,  **kwargs)

        print("Agent:", agent.name)
        for repeat in range(REPEAT_SIMULATION):
            simulator_copy = deepcopy(simulator) # Todo isn't it better to avoid copy paradigm

            # Ask agent for edges to add
            new_edges = agent.get_channels(simulator_copy.get_graph())  # state is just the graph

            # Add edges to a local copy of the simulator
            for edge in new_edges:
                simulator_copy.add_edge(**edge)

            debug_dir = None
            if out_dir is not None:
                debug_dir = os.path.join(out_dir, f"{agent.name}", f"sim-{repeat}")

            start = time()
            simulation_comulative_balance = simulator_copy.run(debug_dir)
            print(f"\t{repeat} {human_format(NUM_TRANSACTIONS/(time()-start))} tnx/sec")

            results[agent.name] += [simulation_comulative_balance]  # peforms NUM_TRANSACTIONS transactions

    colors = ['g', 'b', 'r']
    for i, agent_name in enumerate(results):
        agent_stats = np.array(results[agent_name]) - MAX_AGENT_FUNDS
        mean = agent_stats.mean(0)
        std = agent_stats.std(0)
        # plt.plot(range(len(mean)), mean, label=agent_name, color=colors[i])
        plt.errorbar(range(len(mean)), mean, std, label=agent_name, color=colors[i])
        # TODO use seaborn
        # sns.relplot(x="timepoint", y="signal", kind="line", data=pd.DataFrame(agent_stats));

    plt.legend()
    plt.show()

if __name__ == '__main__':
    args = [(RandomInvestor, {}), (GreedyNodeInvestor, {'use_minimal_cpacity': True})]#, (LightningPlusPlusAgent, {'alpha': 2})]
    # args = [(GreedyNodeInvestor, {'use_minimal_cpacity': True})]
    run_experiment(args, out_dir=SIMULATION_OUT_DIR)
