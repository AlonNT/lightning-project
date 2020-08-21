import os
from collections import defaultdict
from copy import deepcopy
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pickle

from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.RandomAgent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from LightningSimulator import LightningSimulator
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.visualizers import plot_experiment_mean_and_std
from opt import *


def get_simulator():
    """
    Builds the simulator from a simplified version of the lightning dump
    """
    graph = create_sub_graph_by_node_capacity(k=SIMULATOR_NUM_NODES,
                                              highest_capacity_offset=GRAPH_DENSITY_OFFSET)
    simulator = LightningSimulator(graph, num_transactions=SIMULATOR_NUM_TRANSACTIONS,
                                   transfer_amount=SIMULATOR_TRANSFERS_MAX_AMOUNT,
                                   other_balance_proportion=SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION)
    return simulator


def run_experiment(agent_constructors, out_dir, plot_graph_transactions=False):
    """
    Creates a Lightning simulator, common to all of the given agents.
    For each agent:
    1. Ask agent for edges it wants to establish given a funds constraint.
    2. Add edges to a copy of the simulator.
    3. Repeat simulation and plot average results.

    :param agent_constructors: list of tuples of an agent constructor and additional kwargs
    :param out_dir: debug outputs dir
    : plot_graph_transactions:  create visualisaztion image for each transaction (very slow)
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

            verify_channels(new_edges)
            simulator_copy.add_edges(new_edges)

            graph_debug_dir = os.path.join(out_dir, f"{agent.name}", f"sim-{repeat}") if plot_graph_transactions else None

            # Run the simulation
            start = time()
            simulation_cumulative_balance = simulator_copy.run(graph_debug_dir)
            print(f"\t\ttnx/sec: {human_format(SIMULATOR_NUM_TRANSACTIONS / (time() - start))}")
            print(f"\t\tSuccessfull transactions rate: "
                  f"{100*simulator_copy.successfull_transactions / float(SIMULATOR_NUM_TRANSACTIONS)}%")

            results[agent.name].append(simulation_cumulative_balance)

    for k in results:
        results[k] = np.array(results[k]) - INITIAL_FUNDS

    pickle.dump(results, open(os.path.join(out_dir, 'results_dict.pkl'), 'wb'))

    fig, ax = plot_experiment_mean_and_std(results)
    fig.suptitle(get_experiment_description_string(prefix="plot-", delim=", "))
    fig.savefig(os.path.join(out_dir, "Simulator_log.png"))
    plt.show()


def verify_channels(new_edges):
    """
    This function verifies the agent provided channels that do not exceed the funds it was given
    """
    funds_spent = 0
    for edge in new_edges:
        funds_spent += edge['node1_balance'] + LN_DEFAULT_CHANNEL_COST
    assert funds_spent <= INITIAL_FUNDS
    print(f"\t\tEstablishing {len(new_edges)} new edges")
    print(f"\t\tUsed {int(100 * funds_spent / INITIAL_FUNDS)}% of funds")


def get_experiment_description_string(prefix="", delim="_"):
    return f"{prefix}" \
           f"N[{SIMULATOR_NUM_NODES}]" \
           f"{delim}D[{GRAPH_DENSITY_OFFSET}]" \
           f"{delim}F[{human_format(INITIAL_FUNDS)}]" \
           f"{delim}T[{human_format(SIMULATOR_TRANSFERS_MAX_AMOUNT)}]"

if __name__ == '__main__':
    args = [
        # (LightningPlusPlusAgent, {'desired_num_edges': 10}),
        # (LightningPlusPlusAgent, {'desired_num_edges':5}),
        # (LightningPlusPlusAgent, {'desired_num_edges': 10, 'use_node_degree': True}),
        # (LightningPlusPlusAgent, {'desired_num_edges': 10, 'use_node_degree': True, 'minimize': True}),
        (LightningPlusPlusAgent, {'desired_num_edges': 10, 'use_node_routeness': True}),
        (LightningPlusPlusAgent, {'desired_num_edges': 10, 'use_node_routeness': True, 'minimize': True}),
        # (GreedyNodeInvestor, dict()),
        # (GreedyNodeInvestor, {'minimize': True}),
        # (GreedyNodeInvestor, {'use_node_degree': True,'desired_num_edges':4}),
        # # (GreedyNodeInvestor, {'use_node_degree': True, 'minimize': True}),
        (GreedyNodeInvestor, {'use_node_routeness': True}),
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'minimize': True}),
        # (RandomInvestor, {'desired_num_edges': 10}),
        # (RandomInvestor, {'desired_num_edges':10})
    ]

    out_dir = os.path.join(DEBUG_OUT_DIR, get_experiment_description_string())
    os.makedirs(out_dir, exist_ok=True)
    run_experiment(args, out_dir=out_dir, plot_graph_transactions=VISUALIZE_TRANSACTIONS)
