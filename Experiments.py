from Agents.GreedyAgent import GreedyNodeInvestor
from Agents.RandomAgent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from main import get_experiment_description_string, run_experiment
import os
from opt import *
from main import get_simulator
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BASE_FEE_VALUES = [1, 3, 20, 99, 999]


def get_base_fee_percent():
    """
    From the lightning graph dump gets the base fee of the nodes and that calculate the percentile of different percents
    :return: percentile of different percents of the base fee
    """
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

    # Density Plot and Histogram of all arrival delays
    sns.distplot(base_fees, color='darkblue', kde=False,
                 hist_kws={'edgecolor': 'black'},
                 kde_kws={'linewidth': 4})

    # Plot formatting
    plt.legend(prop={'size': 16}, title='Base-fee')
    plt.title('Base-fee')
    plt.xlabel('Base Fee')
    plt.ylabel('Number Of Nodes')
    out_dir = os.path.join("Experiments", "histogram.svg")
    plt.savefig(out_dir)

    return base_fees_percentile


############# Number of Transaction as y-axis ##################


def get_args_experiment_greedy_function_of_transactions_per_step():
    args = [

        (GreedyNodeInvestor, {'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
        (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),

    ]
    return args, "experiment_greedy_function_of_transactions_per_step"


def get_args_experiment_lpp_function_of_transactions_per_step():
    args = [

        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False, 'use_node_routeness': True}),
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False, 'use_node_degree': True}),
    ]
    return args, "experiment_lpp_function_of_transactions_per_step"


def get_args_experiment_random_function_of_transactions_per_step():
    args = [

        (RandomInvestor, {'desired_num_edges': 16}),
    ]
    return args, "experiment_random_function_of_transactions_per_step"


################################# L++ VS. Greedy #################################


def get_args_experiment_greedy_vs_lpp_capacities():
    args_1 = [
        # Capacity
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_nodes_distance': False}),

        (GreedyNodeInvestor, {'desired_num_edges': 16},),
    ]
    return args_1, "experiment_greedy_vs_lpp_capacities"


def get_args_experiment_greedy_vs_lpp_degree():
    args = [
        # Degree
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': False}),

        (GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16}),
    ]
    return args, "experiment_greedy_vs_lpp_degree"


def get_args_experiment_greedy_vs_lpp_routeness():
    args = [
        # Routeness
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_routeness': True, 'use_nodes_distance': False}),

        (GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16}),
    ]
    return args, "experiment_greedy_vs_lpp_routenesse"


################################# L++ Distance - Done #################################

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
    return args, "experiment_distance_lpp"


################################# Policy - Done #################################

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
    return args, "policy_vs_default_policy_in_greedy_agent"


############## TRADEOFF FEES ALL AGENT PER SCORE ##############################

def get_args_experiment_fees_tradeoff_greedy_capacity():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((GreedyNodeInvestor, {'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_greedy_capacity"


def get_args_experiment_fees_tradeoff_greedy_degree():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((GreedyNodeInvestor, {'use_node_degree': True, 'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_greedy_degree"


def get_args_experiment_fees_tradeoff_greedy_routeness():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((GreedyNodeInvestor, {'use_node_routeness': True, 'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_greedy_routeness"


def get_args_experiment_fees_tradeoff_lpp_capacity():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((LightningPlusPlusAgent, {'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_lpp_capacity"


def get_args_experiment_fees_tradeoff_lpp_degree():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((LightningPlusPlusAgent, {'use_node_degree': True, 'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_lpp_degree"


def get_args_experiment_fees_tradeoff_lpp_routeness():
    args = list()
    for fee in BASE_FEE_VALUES:
        args.append((LightningPlusPlusAgent, {'use_nodes_distance': False, 'use_node_routeness': True,
                                              'desired_num_edges': 16, "fee": int(fee)},))
    return args, "fees_tradeoff_lpp_routeness"


def get_args_experiment_best_of_each_agent():
    args = [

        # LPP
        (LightningPlusPlusAgent, {'desired_num_edges': 16, 'use_node_degree': True, 'use_nodes_distance': False}),

        # Greedy
        (GreedyNodeInvestor, {'desired_num_edges': 16, 'use_node_degree': True, }),

        # Random
        (RandomInvestor, {'desired_num_edges': 16}),

    ]
    return args, "experiment_best_of_each_agent"


def run_experiments(experiments):
    dispatcher = {
        'get_args_experiment_greedy_function_of_transactions_per_step':
            get_args_experiment_greedy_function_of_transactions_per_step,
        'get_args_experiment_lpp_function_of_transactions_per_step':
            get_args_experiment_lpp_function_of_transactions_per_step,
        'get_args_experiment_random_function_of_transactions_per_step':
            get_args_experiment_random_function_of_transactions_per_step,

        'get_args_experiment_greedy_vs_lpp_capacities': get_args_experiment_greedy_vs_lpp_capacities,
        'get_args_experiment_greedy_vs_lpp_degree': get_args_experiment_greedy_vs_lpp_degree,
        'get_args_experiment_greedy_vs_lpp_routeness': get_args_experiment_greedy_vs_lpp_routeness,

        'get_args_experiment_best_of_each_agent': get_args_experiment_best_of_each_agent,

        'get_args_experiment_fees_tradeoff_lpp_routeness': get_args_experiment_fees_tradeoff_lpp_routeness,
        'get_args_experiment_fees_tradeoff_greedy_capacity': get_args_experiment_fees_tradeoff_greedy_capacity,
        'get_args_experiment_fees_tradeoff_greedy_degree': get_args_experiment_fees_tradeoff_greedy_degree,

        'get_args_experiment_distance_lpp': get_args_experiment_distance_lpp}

    for experiment in experiments:
        try:
            experiment_function = dispatcher[experiment]
        except KeyError:
            raise ValueError('invalid input')

        args, folder_name = experiment_function()
        print(folder_name)
        out_dir = os.path.join(DEBUG_OUT_DIR, folder_name)
        os.makedirs(out_dir, exist_ok=True)
        run_experiment(args, out_dir=out_dir, plot_graph_transactions=VISUALIZE_TRANSACTIONS)


def main():
    experiments = args.list_of_experiments_names
    run_experiments(experiments)


if __name__ == '__main__':
    main()
