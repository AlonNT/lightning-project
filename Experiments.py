from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.RandomAgent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent


def get_experiment_greedy_vs_lpp():
    args = [
        # Capacity
        (LightningPlusPlusAgent, {'desired_num_edges': 16,  'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False, 'minimize': True}),

        # Degree
        # (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': False}),
        # (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'minimize': True,
        #                           'use_nodes_distance': False}),

        # Routeness
        # (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'use_nodes_distance': False}),
        # (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'minimize': True,
        #                           'use_nodes_distance': False}),

        # Capacity
        (GreedyNodeInvestor, {'desired_num_edges': 16}, ),
        (GreedyNodeInvestor, {'desired_num_edges': 16, 'minimize': True},),

        # Degree
        # (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),
        # (GreedyNodeInvestor, {'use_node_degree': True, 'minimize': True, 'desired_num_edges': 16}),
        #
        # # Routeness
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
        # (GreedyNodeInvestor, {'use_node_routeness': True, 'minimize': True, 'desired_num_edges': 16}),
    ]
    return args


def get_experiment_distance_lpp():
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
