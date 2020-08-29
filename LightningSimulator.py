import os
import random
from typing import List, Dict

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
        src_node_balance_key, dest_node_balance_key = get_nodes_ordered_balance_keys(src, edge_data)

        # Channel Updates with the cumulative fees in the route and the amount to transfer
        edge_data[src_node_balance_key] -= amount + reversed_cumulative_fees[i]
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

    def __init__(self, graph: nx.MultiGraph, num_transactions, transfer_amount, other_balance_proportion, 
                 verbose=False):
        self.graph: nx.MultiGraph = graph
        self.other_balance_proportion = other_balance_proportion
        # For plotting the graph in networkX framework, each node (vertex) has position (x,y)
        self.positions = nx.spring_layout(self.graph)
        self.num_transactions = num_transactions
        self.transfer_amount = transfer_amount
        self.agent_pub_key = None
        self.verbose = verbose
        self.route_memory = dict()
        self.successfull_transactions = 0

    def run(self, plot_dir=None):
        """
        This function runs the experiment, and plot if needed.
        :param plot_dir:
        """
        cumulative_balances = [self.get_node_balance(self.agent_pub_key)]
        numbers_of_routes_via_agent_per_step: List[int] = list()

        for step in range(self.num_transactions):
            # Sample random nodes
            possible_nodes = [node_pub_key for node_pub_key in self.graph.nodes if node_pub_key != self.agent_pub_key]
            node1, node2 = random.sample(possible_nodes, 2)

            if (node1, node2) not in self.route_memory:
                route = get_route(self.graph, node1, node2, self.transfer_amount)
                self.route_memory[(node1, node2)] = route

            route = self.route_memory[(node1, node2)]
            if self.is_agent_in_route(route):
                numbers_of_routes_via_agent_per_step.append(1)

            # If the routing was not successful, nothing to do.
            if route is not None:
                # Gets the index of the last node that can get the money (if the money was
                # transferred, this is node2).
                debug_last_node_index_in_route = transfer_money_in_graph(self.graph, self.transfer_amount, route)
                if debug_last_node_index_in_route == len(route):
                    self.successfull_transactions += 1
                if plot_dir is not None:
                    os.makedirs(plot_dir, exist_ok=True)
                    visualize_graph_state(self.graph, self.positions,
                                          transfer_routes=[(route, debug_last_node_index_in_route)],
                                          out_path=os.path.join(plot_dir, f"step-{step}"),
                                          verify_node_serial_number=False,
                                          plot_title=f"step-{step}")
            cumulative_balances.append(self.get_node_balance(self.agent_pub_key))

        return cumulative_balances, numbers_of_routes_via_agent_per_step

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

    def add_edges(self, edges: List[Dict]):
        """
        Add a list of edges to the graph.
        :param edges: A list of edges to add to the graph.
        """
        for edge in edges:
            self.add_edge(**edge)

    def add_edge(self, node1_pub, node2_pub, node1_policy, node1_balance):
        """
        Adds an edge_to the graph from one node to another.

        :param node1_pub: public_key of node1
        :param node2_pub: public_key of node2
        :param node1_policy:
        :param node1_balance: node1 balance
        """

        node2_balance = self.other_balance_proportion*node1_balance
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

    def is_agent_in_route(self, route):
        """
        Check if agent appear in the route
        :param route: list of edges
        :return: True iff agent is in the route
        """
        for node1, node2, channel_id in route:
            if node1 == self.agent_pub_key:
                return True
        return False
