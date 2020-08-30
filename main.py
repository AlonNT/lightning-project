import os
from collections import defaultdict
from copy import deepcopy
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pickle

from LightningSimulator import LightningSimulator
from utils.common import human_format
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.visualizers import plot_experiment_mean_and_std
from opt import *


def get_simulator():
    """
    Builds the simulator from a simplified version of the lightning dump
    :return: Simulator
    """
    graph = create_sub_graph_by_node_capacity(k=SIMULATOR_NUM_NODES,
                                              highest_capacity_offset=GRAPH_DENSITY_OFFSET)
    simulator = LightningSimulator(graph, num_transactions=SIMULATOR_NUM_TRANSACTIONS,
                                   transfer_amount=SIMULATOR_TRANSFERS_MAX_AMOUNT,
                                   other_balance_proportion=SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION)
    return simulator


def run_experiment(agent_constructors, out_dir, plot_graph_transactions=False, use_number_of_transactions=False):
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
    results_revenue = defaultdict(list)

    # For each agent store a list of lists:
    # Each inner list is the the nuber of transaction that pass via the agent in the  corresponding simulation.
    results_num_transaction = defaultdict(list)

    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class inheriting AbstractAgent
        agent = agent_constructor(public_key=new_node_pub_key,
                                  initial_funds=INITIAL_FUNDS,
                                  channel_cost=LN_DEFAULT_CHANNEL_COST,
                                  **kwargs)

        print("Agent:", agent.name)
        for repeat in range(NUMBER_REPEATED_SIMULATIONS):
            print(f"\trepeat {repeat}:")
            simulator_copy = deepcopy(simulator)

            # Ask agent for edges to add.
            new_edges = agent.get_channels(simulator_copy.graph)

            verify_channels(new_edges)
            simulator_copy.add_edges(new_edges)

            graph_debug_dir = os.path.join(out_dir, f"{agent.name}", f"sim-{repeat}") if plot_graph_transactions else None

            # Run the simulation
            start = time()
            simulation_cumulative_balance, numbers_of_transaction_via_agent = simulator_copy.run(graph_debug_dir)
            print(f"\t\ttnx/sec: {human_format(SIMULATOR_NUM_TRANSACTIONS / (time() - start))}")
            print(f"\t\tSuccessfull transactions rate: "
                  f"{100*simulator_copy.successfull_transactions / float(SIMULATOR_NUM_TRANSACTIONS)}%")

            results_num_transaction[agent.name].append(numbers_of_transaction_via_agent)
            results_revenue[agent.name].append(simulation_cumulative_balance)

        results_num_transaction[agent.name] = np.array(results_num_transaction[agent.name])
        results_revenue[agent.name] = np.array(results_revenue[agent.name]) - INITIAL_FUNDS
        pickle.dump(results_revenue[agent.name], open(os.path.join(out_dir, f'{agent.name}-results_dict.pkl'), 'wb'))

    plot_and_save_graph(results_revenue, "results_revenue_simulator_log", out_dir)
    plot_and_save_graph(results_num_transaction, "results_num_transaction_simulator_log", out_dir)


def plot_and_save_graph(experiment_results, file_name, out_dir):
    fig = plt.figure(figsize=(12, 8))
    ax = plt.subplot(111)
    plot_experiment_mean_and_std(experiment_results, ax)
    ax.legend(loc='upper center', ncol=2)

    fig.suptitle(get_experiment_description_string(prefix="plot-", delim=", "))
    fig.savefig(os.path.join(out_dir, file_name + ".png"))
    fig.savefig(os.path.join(out_dir, file_name + ".svg"))


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
           f"Nodes[{SIMULATOR_NUM_NODES}]" \
           f"{delim}Density[{GRAPH_DENSITY_OFFSET}]" \
           f"{delim}IFunds[{human_format(INITIAL_FUNDS)}]" \
           f"{delim}TAmount[{human_format(SIMULATOR_TRANSFERS_MAX_AMOUNT)}]" \
           f"{delim}CCost[{human_format(LN_DEFAULT_CHANNEL_COST)}]" \
           f"{delim}NTransfer[{human_format(SIMULATOR_NUM_TRANSACTIONS)}]"
