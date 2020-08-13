from typing import Tuple, Dict, List

import networkx as nx
import numpy as np


class CyclicList:
    def __init__(self, items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index % len(self.items)]


PLT_COLORS = CyclicList(['r', 'g', 'b', 'k', 'y', 'k', 'c', 'm'])
LND_DEFAULT_POLICY = {"time_lock_delta": 144, "fee_base_msat": 1000, "proportional_fee": 0.001}


def human_format(num):
    """
    :param num: A number to print in a nice readable way.
    :return: A string representing this number in a readable way (e.g. 1000 --> 1K).
    """
    magnitude = 0

    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])  # add more suffices if you need them


def get_new_position_for_agent_node(positions: Dict):
    """
    Find a new position for the new node in the graph (the agent's node).
    The new position will be the rightmost node, in the middle of the y-axis.
    :param positions: A dictionary of positions per node.
    :return: A NumPy array containing the new position.
    """
    positions_array = np.array([x for x in positions.values()])
    new_position = np.array([positions_array[:, 0].max() + 0.5, positions_array[:, 1].mean()])
    return new_position


def get_sender_policy_and_id(receiver_node_id, edge_data: Dict) -> Tuple:
    """
    :param receiver_node_id: The receiver node id (i.e. public-key).
    :param edge_data: A dictionary containing the edge's attributes.
    :return: A tuple containing two elements:
                 (1) The policy of the sender (A dictionary containing the fee policy)
                 (2) The id (i.e. public-key) of the sender.
    """
    # Check which index is the sender node
    if receiver_node_id == edge_data['node1_pub']:
        sender_node_i = 2
    elif receiver_node_id == edge_data['node2_pub']:
        sender_node_i = 1
    else:
        raise ValueError(f'The given receiver_node_id {receiver_node_id} is not in the given edge_data {edge_data}.')

    # Gets the policy and the index of the sender node
    sender_node_policy = edge_data[f'node{sender_node_i}_policy']
    sender_node_id = edge_data[f'node{sender_node_i}_pub']

    return sender_node_policy, sender_node_id


def calculate_route_fees(graph: nx.MultiGraph, route: List, amount: int, get_debug_str: bool = False):
    """
    Calculate the route fees, based on the policies of the nodes on the route.
    This is done for checking if the money transfer is valid according to the amount and fee in each channel.

    :param graph: The graph to work on.
    :param route: List of edges (tuples of 3: 3 nodes and the channel id).
                  Each edge's two nodes are ordered like source, target.
                  So in total the source of the transfer is the source of the first edge,
                  and the target of the transfer is the target of the last edge.
    :param amount: The amount of money to transfer in the route.
    :param get_debug_str: It true, return a string which is used for debugging purposes.
    :return: The fees for each node in the route.
    """
    total_amount = amount
    fees = list()
    debug_str = " "

    # Traverse the reversed route (list of edges) from the target to the source and sum the fee in each step.
    for edge_key in route[::-1]:
        sender_policy, _ = get_sender_policy_and_id(receiver_node_id=edge_key[1], edge_data=graph.edges[edge_key])

        # Gets the fee in this channel
        fee = sender_policy['fee_base_msat'] + int(total_amount * sender_policy['proportional_fee'])
        if get_debug_str:
            debug_str = f"({human_format(sender_policy['fee_base_msat'])} + " \
                        f"{human_format(total_amount)}*{sender_policy['proportional_fee']})={fee} + " + \
                        debug_str
        fees.append(fee)
        total_amount += fee

    if get_debug_str:
        return fees[::-1], debug_str

    return fees[::-1]


def calculate_agent_policy(graph, node):
    """
    Calculate a policy with minimal values out of all the edge-policies of the given node in edges touching it
    :param graph: lightning graph
    :param node: tuple of the edge data (node1, node2, channel_data)
    :return: min_time_lock_delta, min_base_fee, min_proportional_fee for the agent policy
    """

    # TODO Alon maybe not take the minimal our of these?
    min_base_fee = float('inf')
    min_proportional_fee = float('inf')
    min_time_lock_delta = float('inf')

    for node1, node2, channel_data in graph.edges(node, data=True):
        node_i = 1 if node == channel_data['node1_pub'] else 2
        node_policy = channel_data[f'node{node_i}_policy']

        # TODO Alon are there more values to take into account?
        base_fee = node_policy['fee_base_msat']
        proportional_fee = node_policy['proportional_fee']
        time_lock_delta = node_policy['time_lock_delta']

        min_base_fee = min(min_base_fee, base_fee)
        min_proportional_fee = min(min_proportional_fee, proportional_fee)
        min_time_lock_delta = min(min_time_lock_delta, time_lock_delta)

    return min_time_lock_delta, min_base_fee, min_proportional_fee
