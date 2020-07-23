from typing import Tuple, Dict
import numpy as np

# from LightningGraph.lightning_implementation_inference import CLTV_DELTA_DEFAULTS, HTLC_MIN_DEFAULTS, FEE_DEFAULTS


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def get_new_position_for_node(positions):
    arr = np.array([x for x in positions.values()])
    new_pos = np.array([arr[:,0].max() + 0.5, arr[:,1].mean()])
    # new_pos =  np.clip(arr.max(0) + 0.5, -np.inf, 1)
    return new_pos


def get_sender_policy_and_id(receiver_node_id, edge_data: Dict) -> Tuple:
    """
    :param receiver_node_id: The receiver node id (i.e. public-key).
    :param edge_data: A dictionary containing the edge's attributes.
    :return: A tuple containing two elements:
                 (1) The policy of the sender (A dictionary containing the fee policy)
                 (2) The id (i.e. public-key) of the sender.
    """
    if receiver_node_id == edge_data['node1_pub']:
        sender_node_i = 2
    elif receiver_node_id == edge_data['node2_pub']:
        sender_node_i = 1
    else:
        raise ValueError(f'The given receiver_node_id {receiver_node_id} is not in the given edge_data {edge_data}.')

    sender_node_policy = edge_data[f'node{sender_node_i}_policy']
    sender_node_id = edge_data[f'node{sender_node_i}_pub']

    return sender_node_policy, sender_node_id


def calculate_route_fees(graph, route, amount, get_debug_str=False):
    total_amount = amount
    fees = []
    debug_str = " "
    for edge_key in route[::-1]:
        sender_policy, _ = get_sender_policy_and_id(edge_key[1], graph.edges[edge_key])
        fee = int(sender_policy['fee_base_msat'] + (total_amount * sender_policy['fee_rate_milli_msat']))
        if get_debug_str:
            debug_str = f"({human_format(sender_policy['fee_base_msat'])} + {human_format(total_amount)}*{sender_policy['fee_rate_milli_msat']})={fee} + " + debug_str
        fees += [fee]
        total_amount += fee
    if get_debug_str:
        return fees[::-1], debug_str
    return fees[::-1]