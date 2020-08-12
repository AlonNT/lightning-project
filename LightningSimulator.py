import os
import random
from typing import List

import networkx as nx
import numpy as np

from routing.LND_routing import get_route
from utils.common import LND_DEFAULT_POLICY
from utils.common import calculate_route_fees, get_new_position_for_agent_node
from utils.visualizers import visualize_graph_state


def transfer_money_in_graph(graph: nx.MultiGraph, amount: int, route: List, verbose: bool = False) -> int:
    """
    Perform transfer of money along a route in a given graph.
    It makes sure the transaction is possible, and change channels' balances along the route accordingly.

    :param graph: The graph to work on.
    :param amount: Amount to transfer.
    :param route: List of edges (tuples of 3: 3 nodes and the channel id).
                  Each edge's two nodes are ordered like source, target.
                  So in total the source of the transfer is the source of the first edge,
                  and the target of the transfer is the target of the last edge.
    :param verbose: If true, prints progress.
    :return: int: len(route) if transaction succeeded
                  Otherwise, it returns some index i such that 0 < i < len(route) to indicate
                  the first encountered node that wasn't able to transfer the funds.
    """
    if verbose:
        first_edge = route[0]
        last_edge = route[-1]
        src_serial_num = graph.nodes[first_edge[0]]['serial_number']
        dst_serial_num = graph.nodes[last_edge[1]]['serial_number']
        print(f"\tManager | Trying to transfer {amount} from node({src_serial_num}) to node({dst_serial_num})")

    fees_list = calculate_route_fees(graph, route, amount)
    reversed_cumulative_fees = np.cumsum(fees_list)[::-1]

    # Traverse the channels and check if the amount can pass through them.
    # In case the amount is valid to transfer, update the balances of the channels.
    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        src_node_balance_keys, dest_node_balance_key = get_nodes_ordered_balance_keys(src, edge_data)
        src_node_balance, dst_node_balance = edge_data[src_node_balance_keys], edge_data[dest_node_balance_key]

        if src_node_balance < amount + reversed_cumulative_fees[i]:
            if verbose:
                print(f"\tManager | Failed! not enough funds in node({graph.nodes[src]['serial_number']})"
                      f" ({src_node_balance} < {amount + reversed_cumulative_fees[i]})")
            return i

    # amount transfer is valid, and hence updating the channels with new amounts.
    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        src_node_balance_keys, dest_node_balance_key = get_nodes_ordered_balance_keys(src, edge_data)

        # Channel Updates with the cumulative fees in the route and the amount to transfer
        edge_data[src_node_balance_keys] -= amount + reversed_cumulative_fees[i]
        edge_data[dest_node_balance_key] += amount + reversed_cumulative_fees[i]

    if verbose:
        print("\tManager | Transferred!!!")

    return len(route)


def get_nodes_ordered_balance_keys(src, edge_data):
    """
    This functions gets the source node in the route and return which node is it (node1 ot node2 in the channel)
    :param src: src node in the route
    :param edge_data: dictionary containing the edge's attributes.
    :return: the order of the nodes in the money transformation
    """
    if edge_data['node1_pub'] == src:
        return 'node1_balance', 'node2_balance'
    return 'node2_balance', 'node1_balance'


class LightningSimulator:
    """
    This is a simulator for the different agents - each tries to maximize its revenue from the fees it gets.
    """

    def __init__(self, graph: nx.MultiGraph, num_transfers, transfer_max_amount, verbose=False):
        self.graph: nx.MultiGraph = graph

        # For plotting the graph in networkX framework, each node (vertex) has position (x,y)
        self.positions = nx.spring_layout(self.graph)
        self.num_transfers = num_transfers
        self.transfer_max_amount = transfer_max_amount
        self.agent_pub_key = None
        self.verbose = verbose

    def run(self, plot_dir=None):
        """
        This function runs the experiment, and plot if needed.
        :param plot_dir:
        """
        cumulative_balances = [self.get_node_balance(self.agent_pub_key)]

        for step in range(self.num_transfers):
            # TODO Ariel - is it on purpose that there are only two possible amounts?
            # TODO it's self.transfer_max_amount - 1 or self.transfer_max_amount...
            amount = random.randint(self.transfer_max_amount - 1, self.transfer_max_amount)

            # Sample random nodes
            possible_nodes = [node_pub_key for node_pub_key in self.graph.nodes if node_pub_key != self.agent_pub_key]
            node1, node2 = random.sample(possible_nodes, 2)

            # Get the route from node1 to node2 with the routing algorithm and transfer the money.
            route = get_route(self.graph, node1, node2, amount)

            # If the routing was not successful, nothing to do.
            if route is not None:
                # Gets the index of the last node that can get the money (if the money was
                # transferred, this is node2).
                debug_last_node_index_in_route = transfer_money_in_graph(self.graph, amount, route)
                if plot_dir is not None:
                    os.makedirs(plot_dir, exist_ok=True)
                    visualize_graph_state(self.graph, self.positions,
                                          transfer_routes=[(route, debug_last_node_index_in_route)],
                                          out_path=os.path.join(plot_dir, f"step-{step}"),
                                          verify_node_serial_number=False,
                                          plot_title=f"step-{step}",  # TODO delete the following commented-out code?
                                          additional_node_info=None)  # {self.agent_pub_key: f"Agent balance: {agent_reward}"})
            cumulative_balances.append(self.get_node_balance(self.agent_pub_key))

        return cumulative_balances

    def create_agent_node(self):
        """
        Add new node to the graph
        :return: The public key of the new node
        """
        if self.agent_pub_key is not None:
            raise ValueError("Simulator currently supports one agent and one node addition")

        # Check how many nodes is in the graph (X) and define the serial number of the new nodes as X + 1
        serial_num = len(self.graph.nodes) + 1
        pub_key = "Agent-" + str(serial_num)

        # Add the node to networkX graph
        self.graph.add_node(pub_key, pub_key=pub_key, serial_number=serial_num, total_capacity=0)

        # Define the position of the new node (for plotting the networkX graph)
        self.positions[pub_key] = get_new_position_for_agent_node(self.positions)

        self.agent_pub_key = pub_key
        return pub_key

    def get_node_balance(self, node_public_key):
        """
        This function traverse through all the neighbors of a specific node and sum the money
        it has in each channel.
        :param node_public_key: public_key of the node
        :return: Sums the balances of the node from all his channels.
        """
        total_balance = 0

        # Get the connected edges of this node and traverse them and sum the balance.
        connected_edges = self.graph.edges(node_public_key, data=True)
        for _, _, edge_data in connected_edges:
            node_i = 1 if (node_public_key == edge_data['node1_pub']) else 2
            total_balance += edge_data[f'node{node_i}_balance']

        return total_balance

    def add_edges(self, edges: List):
        """
        Add a list of edges to the graph.
        :param edges: A list of edges to add to the graph.
        """
        for edge in edges:
            self.add_edge(**edge)

    def add_edge(self, node1_pub, node2_pub, node1_policy, node1_balance, node2_balance):
        """
        Adds an edge_to the graph from one node to another.

        :param node1_pub: public_key of node1
        :param node2_pub: public_key of node2
        :param node1_policy:
        :param node1_balance: node1 balance
        :param node2_balance: node2 balance
        """
        if self.verbose:
            print(f"\tManager | Adding edge between "
                  f"node({self.graph.nodes[node1_pub]['serial_number']})"
                  f" and node({self.graph.nodes[node2_pub]['serial_number']})")

        capacity = node1_balance + node2_balance
        channel_id = str(len(self.graph.edges) + 1)

        self.graph.add_edge(node1_pub, node2_pub, key=channel_id,
                            channel_id=channel_id, node1_pub=node1_pub, node2_pub=node2_pub,
                            node1_policy=node1_policy, node2_policy=LND_DEFAULT_POLICY,
                            capacity=capacity, node1_balance=node1_balance, node2_balance=node2_balance)

        # Updates the total capacity according to the new channel capacity
        for node_pub in [node1_pub, node2_pub]:
            self.graph.nodes[node_pub]['total_capacity'] += capacity
