from utils.common import calculate_route_fees
import numpy as np


def transfer_money_in_graph(graph, amount: int, route, verbose=False):
    """
    Preform transformation of money between two nodes
    :param amount: amount to transfer
    :param route: list of edges
    :return:
    """
    if verbose:
        debug_src_serial_num = graph.nodes[route[0][0]]['serial_number']
        debug_dst_serial_num = graph.nodes[route[-1][1]]['serial_number']
        print(f"\tManager | Trying to transfer {amount} "
              f"mast from node({debug_src_serial_num}) to node({debug_dst_serial_num})")

    fees_list = calculate_route_fees(graph, route, amount)
    cumulaive_fees = np.cumsum(fees_list)[::-1]
    # Transformation of the first channel is the total fees

    # Traverse the channels and check if the amount can pass through them.
    # In case the amount is valid to transfer, update the balances of the channels
    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        if edge_data['node1_pub'] == src:
            src_node_balance, dst_node_balance = edge_data['node1_balance'], edge_data['node2_balance']
        else:
            src_node_balance, dst_node_balance = edge_data['node2_balance'], edge_data['node1_balance']

        if src_node_balance < amount + cumulaive_fees[i]:
            if verbose:
                print(f"\tManager | Failed! not enough funds in node({graph.nodes[src]['serial_number']})"
                      f" ({src_node_balance} < {amount + cumulaive_fees[i]})")
            return route[0][0], route[-1][1], route, i

    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        if edge_data['node1_pub'] == src:
            src_node_balance_name, dst_node_balance_name = 'node1_balance', 'node2_balance'
        else:
            src_node_balance_name, dst_node_balance_name = 'node2_balance', 'node1_balance'
        # Channel Updates
        edge_data[src_node_balance_name] -= amount + cumulaive_fees[i]
        edge_data[dst_node_balance_name] += amount + cumulaive_fees[i]

    if verbose:
        print("\tManager | Transferred!!")
    return route[0][0], route[-1][1], route, len(route)