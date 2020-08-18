import os
from collections import defaultdict
from copy import deepcopy
from time import time

import matplotlib.pyplot as plt
import numpy as np

from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.RandomAgent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from LightningSimulator import LightningSimulator
from utils.common import PLT_COLORS
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.visualizers import plot_experiment_mean_and_std

# ============== Experiment Configuration ============== #
# TODO # bitcoint == 10**8 satoshies but it seems like the fees are working with msat sot is it bitcoin == 10*11 msat ?
# The initial funds of the agents.
INITIAL_FUNDS = 10 ** 9

# The maximal amount that can be transferred between two nodes.
SIMULATOR_TRANSFERS_MAX_AMOUNT = 5*10 ** 6

# defines the balance in the other side of new channels in proportion of the first side balance
SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION = 1.0

# How many transaction the simulator will simulate.
SIMULATOR_NUM_TRANSACTIONS = 10000

# How many times to repeat the experiment, in order to get the mean & std of the reward in each step.
NUMBER_REPEATED_SIMULATIONS = 3

# The size of the sub-graph of the lightning network to simulate.
SIMULATOR_NUM_NODES = 100

# The higher this number the more sparse the sub-graph is.
# The nodes will be ordered by some metric and the M next nodes will be selected.
GRAPH_DENSITY_OFFSET = 50

DEBUG_OUT_DIR = None

# The channel creation cost (which is the cost payed for the bitcoin miners
# to include the channel's creation transaction in their block).
# This value changes constantly (due to the dynamics of the bitcoin transactions' fees
# that change according to the load on the blockchain).
# This approximate value was calculated using buybitcoinworldwide.com to get the cost
# of a transaction (in usd), then converting us dollars to satoshis (in 8.8.2020).
LN_DEFAULT_CHANNEL_COST = 4 * 10 ** 4


def get_simulator():
    """
    Builds the simulator from a simplified version of the lightning dump
    """
    graph = create_sub_graph_by_node_capacity(k=SIMULATOR_NUM_NODES,
                                              highest_capacity_offset=GRAPH_DENSITY_OFFSET)
    simulator = LightningSimulator(graph, num_transfers=SIMULATOR_NUM_TRANSACTIONS,
                                   transfer_max_amount=SIMULATOR_TRANSFERS_MAX_AMOUNT,
                                   other_balance_proportion=SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION)
    return simulator


def run_experiment(agent_constructors, out_dir=None):
    """
    Creates a Lightning simulator, common to all of the given agents.
    For each agent:
    1. Ask agent for edges it wants to establish given a funds constraint.
    2. Add edges to a copy of the simulator.
    3. Repeat simulation and plot average results.

    :param agent_constructors: list of tuples of an agent constructor and additional kwargs
    :param out_dir: optional directory for plotting debug images of the simulation, off if None
    """
    # Create the base Simulator which will be copied for each simulation
    simulator = get_simulator()
    new_node_pub_key = simulator.create_agent_node()

    # For each agent store a list of lists:
    # Each inner list is the cumulative revenues for the corresponding simulation.
    results = defaultdict(list)

    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class inheriting AbstractAgent
        agent = agent_constructor(public_key=new_node_pub_key,
                                  initial_funds=INITIAL_FUNDS,
                                  channel_cost=LN_DEFAULT_CHANNEL_COST,
                                  **kwargs)

        print("Agent:", agent.name)
        for repeat in range(NUMBER_REPEATED_SIMULATIONS):
            print(f"\trepeat {repeat}:")
            simulator_copy = deepcopy(simulator)  # Todo isn't it better to avoid copy paradigm

            # Ask agent for edges to add.
            new_edges = agent.get_channels(simulator_copy.graph)

            verify_channles(new_edges)
            simulator_copy.add_edges(new_edges)

            debug_dir = None if out_dir is None else os.path.join(out_dir, f"{agent.name}", f"sim-{repeat}")

            # Run the simulation
            start = time()
            simulation_cumulative_balance = simulator_copy.run(debug_dir)
            print(f"\t\t{human_format(SIMULATOR_NUM_TRANSACTIONS / (time() - start))} tnx/sec")

            results[agent.name].append(simulation_cumulative_balance)

    # Plot experiments
    for i, agent_name in enumerate(results):
        agent_stats = np.array(results[agent_name]) - INITIAL_FUNDS
        plot_experiment_mean_and_std(agent_stats, label=agent_name, color=PLT_COLORS[i])


    plt.title(f"#Nodes: {human_format(SIMULATOR_NUM_NODES)}, Density: {human_format(GRAPH_DENSITY_OFFSET)},"
              f" Funds: {human_format(INITIAL_FUNDS)}, tx-amount: {human_format(SIMULATOR_TRANSFERS_MAX_AMOUNT)}")
    plt.legend()
    plt.show()


def verify_channles(new_edges):
    """
    This function verifies the agent provided channels that do not exceed the funds it was given
    """
    funds_spent = 0
    for edge in new_edges:
        funds_spent += edge['node1_balance'] + LN_DEFAULT_CHANNEL_COST
    assert funds_spent <= INITIAL_FUNDS
    print(f"\t\tEstablishing {len(new_edges)} new edges")
    print(f"\t\tUsed {int(100 * funds_spent / INITIAL_FUNDS)}% of funds")

if __name__ == '__main__':
    args = [
        (LightningPlusPlusAgent, {'desired_num_edges':20}),
        (LightningPlusPlusAgent, {'desired_num_edges':5}),
        # (GreedyNodeInvestor, dict()),
        # (GreedyNodeInvestor, {'minimize': True}),
        # (GreedyNodeInvestor, {'use_node_degree': True}),
        # (GreedyNodeInvestor, {'use_node_degree': True, 'minimize': True}),
        # (GreedyNodeInvestor, {'use_node_routeness': True}),
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'minimize': True}),
        (RandomInvestor, {'desired_num_edges':20}),
        (RandomInvestor, {'desired_num_edges':5})
    ]

    run_experiment(args, out_dir=DEBUG_OUT_DIR)
