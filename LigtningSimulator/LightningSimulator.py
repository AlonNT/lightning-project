import random

import networkx as nx
import numpy as np

from typing import List

from consts import LND_DEFAULT_POLICY
from routing.LND_routing import get_route
from utils.common import calculate_route_fees, get_new_position_for_node
from utils.visualizers import visualize_graph_state


def transfer_money_in_graph(graph: nx.MultiGraph, amount: int, route: List, verbose: bool = False) -> int:
    """
    Preform transformation of money along a route in a given graph, namely to make sure transaction is possible
    and change channel balances along the route accordingly.

    :param graph: The graph to work on.
    :param amount: Amount to transfer.
    :param route: List of edges (tuples of 2 nodes)
    :param verbose: If true, prints progress
    :return: int: len(route) if transaction succeeded
                  some index i such that 0 < i < len(route) to indicate the first encountered node
                  that wasn't able to transfer the funds.
    """
    if verbose:
        first_edge = route[0]
        last_edge = route[-1]
        src_serial_num = graph.nodes[first_edge[0]]['serial_number']
        dst_serial_num = graph.nodes[last_edge[1]]['serial_number']
        print(f"\tManager | Trying to transfer {amount} from node({src_serial_num}) to node({dst_serial_num})")

    fees_list = calculate_route_fees(graph, route, amount)
    cumulative_fees = np.cumsum(fees_list)[::-1]
    # Transformation of the first channel is the total fees

    # Traverse the channels and check if the amount can pass through them.
    # In case the amount is valid to transfer, update the balances of the channels
    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        if edge_data['node1_pub'] == src:
            src_node_balance, dst_node_balance = edge_data['node1_balance'], edge_data['node2_balance']
        else:
            src_node_balance, dst_node_balance = edge_data['node2_balance'], edge_data['node1_balance']

        if src_node_balance < amount + cumulative_fees[i]:
            if verbose:
                print(f"\tManager | Failed! not enough funds in node({graph.nodes[src]['serial_number']})"
                      f" ({src_node_balance} < {amount + cumulative_fees[i]})")
            return i

    for i, (src, dest, channel_id) in enumerate(route):
        edge_data = graph.edges[(src, dest, channel_id)]
        if edge_data['node1_pub'] == src:
            src_node_balance_name, dst_node_balance_name = 'node1_balance', 'node2_balance'
        else:
            src_node_balance_name, dst_node_balance_name = 'node2_balance', 'node1_balance'
        # Channel Updates
        edge_data[src_node_balance_name] -= amount + cumulative_fees[i]
        edge_data[dst_node_balance_name] += amount + cumulative_fees[i]

    if verbose:
        print("\tManager | Transferred!!")
    return len(route)


class LightningSimulator:
    """This object is an openAI-like environment: its internal state is the Lightning graph and it sumulates flow in
    it at each step.
    """

    def __init__(self, graph: nx.MultiGraph, num_transfers, transfer_max_amount, verbose=False):
        self.graph: nx.MultiGraph = graph
        self.positions = nx.spring_layout(self.graph, seed=None)
        self.num_transfers = num_transfers
        self.transfer_max_amount = transfer_max_amount
        self.agent_pub_key = None
        self.verbose = verbose
        self.logdir = None

    def get_graph(self) -> nx.MultiGraph:
        """
        Returns the internal state of this environment
        """
        return self.graph

    def run(self):
        """
        This function gets an action from the agent changes the internal state accordingly and returns the new state
        :param action: action from the agent a tuple containing
        (desired environment function, desired function arguments)
        :return: the new state
        """

        for step in range(self.num_transfers):
            amount = random.randint(self.transfer_max_amount - 1, self.transfer_max_amount)

            # # Sample long route for debugging
            # from utils.graph_helpers import sample_long_route
            # route, src, dest = sample_long_route(self.graph, amount, get_route, min_route_length=4)

            # sample random nodes
            choice_nodes = [node_pub_key for node_pub_key in self.graph.nodes if node_pub_key != self.agent_pub_key]
            nodes = random.sample(choice_nodes, 2)
            route = get_route(self.graph, nodes[0], nodes[1], amount)
            if route is not None:
                debug_last_index = transfer_money_in_graph(self.graph, amount, route)
                if self.logdir is not None:
                    visualize_graph_state(self.graph, self.positions,
                                          transfer_routes=[(route, debug_last_index)],
                                          out_dir=self.logdir, # TODO get it from arguments
                                          verify_node_serial_number=False,
                                          plot_title=f"step-{step}",
                                          additional_node_info=None) #{self.agent_pub_key: f"Agent balance: {agent_reward}"})

    def create_agent_node(self):
        """
        Add new node to the graph
        :return: The public key of the new node
        """
        serial_num = len(self.graph.nodes) + 1
        pub_key = "Agent-" + str(serial_num)
        self.graph.add_node(pub_key, pub_key=pub_key, serial_number=serial_num)
        self.positions[pub_key] = get_new_position_for_node(self.positions)
        if self.agent_pub_key is not None:
            raise Warning("Environment currently supports one agent and one node addition")
        self.agent_pub_key = pub_key
        return pub_key

    def get_node_balance(self, node_pub_key):
        """Sum the balances of the node from all his channels"""
        total_balance = 0
        connected_edges = self.graph.edges(node_pub_key, data=True)
        for _, _, edge_data in connected_edges:
            if node_pub_key == edge_data['node1_pub']:
                total_balance += edge_data['node1_balance']
            else:
                total_balance += edge_data['node2_balance']
        return total_balance


    def add_edge(self, node1_pub, node2_pub, node1_policy, node1_balance, node2_balance):
        """
        Adds an edge_to the graph
        Todo: currently the action sener can switch the pukeys order and choose the other side's policy which is wiered
        :param public_key_node1:
        :param public_key_node2:
        :param node1_balance:
        :param node2_balance:
        :return:
        """
        if self.verbose:
            print(f"\tManager | Adding edge between node({self.graph.nodes[node1_pub]['serial_number']})"
                  f" and node({self.graph.nodes[node2_pub]['serial_number']})")
        capacity = node1_balance + node2_balance
        channel_id = str(len(self.graph.edges) + 1)
        self.graph.add_edge(node1_pub, node2_pub, channel_id,  # This is ok for multigraphs
                            channel_id=channel_id, node1_pub=node1_pub, node2_pub=node2_pub,
                            node1_policy=node1_policy, node2_policy=LND_DEFAULT_POLICY,
                            capacity=capacity, node1_balance=node1_balance, node2_balance=node2_balance)
        # Todo : update node2 total capacity
