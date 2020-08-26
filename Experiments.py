from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.RandomAgent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from main import get_experiment_description_string, run_experiment
import os
from opt import *


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
        # (GreedyNodeInvestor, {'desired_num_edges': 16},),
        (GreedyNodeInvestor, {'desired_num_edges': 16, 'use_default_policy': False},),

        # # Degree
        # (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),
        # (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16, 'use_default_policy': False}),
        #
        # # Routeness
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'use_default_policy': False, 'desired_num_edges': 16}),

    ]
    return args


if __name__ == '__main__':
    args = [
        # get_args_experiment_greedy_vs_lpp_capacities(),
        # get_args_experiment_greedy_vs_lpp_degree(),
        # get_args_experiment_greedy_vs_lpp_routeness(),
        # get_args_experiment_distance_lpp(),
        get_args_experiment_policy_vs_default_policy_in_greedy_agent()
    ]

    for arg in args:
        out_dir = os.path.join(DEBUG_OUT_DIR, get_experiment_description_string())
        os.makedirs(out_dir, exist_ok=True)
        run_experiment(arg, out_dir=out_dir, plot_graph_transactions=VISUALIZE_TRANSACTIONS)
