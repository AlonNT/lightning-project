from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from main import get_experiment_description_string, run_experiment
import os
from opt import *
from main import get_simulator
import numpy as np


def get_base_fee_percent():
    simulator = get_simulator()
    base_fees = list()

    # From 50% the base fee is 1000 from 10% down is 0 fee
    percent_list = [20, 25, 35, 40, 50]
    base_fees_percentile = list()

    for node1, node2, channel_data in simulator.graph.edges(data=True):
        node_1_base_fee = channel_data['node1_policy']['fee_base_msat']
        node_2_base_fee = channel_data['node2_policy']['fee_base_msat']

        base_fees.append(node_1_base_fee)
        base_fees.append(node_2_base_fee)

    base_fees = np.array(base_fees)

    for percent in percent_list:
        base_fees_percentile.append(np.percentile(base_fees, percent))

    return base_fees_percentile


def get_args_experiment_greedy_vs_lpp_capacities():
    args_1 = [
        # Capacity
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False, 'minimize': True}),

        (GreedyNodeInvestor, {'desired_num_edges': 16},),
        (GreedyNodeInvestor, {'desired_num_edges': 16, 'minimize': True},)]
    return args_1


def get_args_experiment_greedy_vs_lpp_degree():
    args_2 = [
        # Degree
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'minimize': True,
                                  'use_nodes_distance': False}),

        (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_degree': True, 'minimize': True, 'desired_num_edges': 16}),
    ]
    return args_2


def get_args_experiment_greedy_vs_lpp_routeness():
    args_3 = [
        # Routeness
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'minimize': True,
                                  'use_nodes_distance': False}),

        (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_routeness': True, 'minimize': True, 'desired_num_edges': 16}),
    ]
    return args_3


def get_args_experiment_distance_lpp():
    args = [
        # Capacity
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': True}),

        # Degree
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': True}),

        # Routeness
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'use_nodes_distance': True}),

    ]
    return args


def get_args_experiment_policy_vs_default_policy_in_greedy_agent():
    args = [
        # Capacity

        (GreedyNodeInvestor, {'desired_num_edges': 16, 'use_default_policy': False},),
        (GreedyNodeInvestor, {'desired_num_edges': 16},),

        # # Degree
        (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16, 'use_default_policy': False}),

        # Routeness
        (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_routeness': True, 'use_default_policy': False, 'desired_num_edges': 16}),

    ]
    return args


def get_args_experiment_fees_tradeoff():

    base_fees_values = get_base_fee_percent()
    args = list()
    for fee in base_fees_values:
        args.append((GreedyNodeInvestor, {'desired_num_edges': 16, "fee": int(fee)},))
        # args.append((GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16, "fee": int(fee)},))
        # args.append((GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16, "fee": int(fee)},))
    return args

if __name__ == '__main__':
    args = [
        get_args_experiment_greedy_vs_lpp_capacities(),
        get_args_experiment_greedy_vs_lpp_degree(),
        get_args_experiment_greedy_vs_lpp_routeness(),
        # get_args_experiment_distance_lpp(),
        # get_args_experiment_policy_vs_default_policy_in_greedy_agent()
        get_args_experiment_fees_tradeoff()
    ]

    for i, arg in enumerate(args):
        name = "danielafrimi" + str(i) + get_experiment_description_string()
        out_dir = os.path.join(DEBUG_OUT_DIR, name)
        os.makedirs(out_dir, exist_ok=True)
        run_experiment(arg, out_dir=out_dir, plot_graph_transactions=VISUALIZE_TRANSACTIONS)
