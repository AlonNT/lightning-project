import networkx as nx
from typing import List
from LightningGraph.utils import calculate_route_fees, sample_long_route
import numpy as np
import random
from routing.LND_routing import get_route


class Manager:
    def __init__(self, graph: nx.Graph, tranfers_per_step=1, transfer_max_amount=10000):
        self.graph: nx.Graph = graph
        self.tranfers_per_step = tranfers_per_step
        self.transfer_max_amount = transfer_max_amount
        self.num_steps = 0

    def transfer(self, amount: int, route) -> bool:
        """
        Preform transformation of money between two nodes
        :param amount: amount to transfer
        :param src:
        :param dst:
        :return:
        """

        fees_list = calculate_route_fees(self.graph, route, amount)
        cumulaive_fees = np.cumsum(fees_list)[::-1]
        # Transformation of the first channel is the total fees

        # Traverse the channels and check if the amount can pass through them.
        # In case the amount is valid to transfer, update the balances of the channels
        for i, (src, dest, channel_id) in enumerate(route):
            edge_data = self.graph.edges[(src, dest, channel_id)]
            if edge_data['node1_pub'] == src:
                src_node_balance, dst_node_balance = edge_data['node1_balance'], edge_data['node2_balance']
            else:
                src_node_balance, dst_node_balance = edge_data['node2_balance'], edge_data['node1_balance']

            if src_node_balance < amount + cumulaive_fees[i]:
                return False

        for i, (src, dest, channel_id) in enumerate(route):
            edge_data = self.graph.edges[(src, dest, channel_id)]
            if edge_data['node1_pub'] == src:
                src_node_balance_name, dst_node_balance_name = 'node1_balance', 'node2_balance'
            else:
                src_node_balance_name, dst_node_balance_name = 'node2_balance', 'node1_balance'
            # Channel Updates
            edge_data[src_node_balance_name] -= amount + cumulaive_fees[i]
            edge_data[dst_node_balance_name] += amount + cumulaive_fees[i]

        return True

    def get_state(self):
        return self.graph

    def step(self, action) -> nx.Graph:
        """
        This function gets an action from the agent and preform a step
        :param action: action from the agent
        :return: The current Graph
        """
        function_name, args = action

        # if function_name == "add_edge":
        #     self.add_edge(*args)
        # elif function_name == "NOOP":
        #     pass
        # else:
        #     raise ValueError(f"{function_name} not supported ")

        for step in range(self.tranfers_per_step):
            amount = random.randint(100, self.transfer_max_amount)

            # Sample long route for debugging
            route = sample_long_route(self.graph, amount, get_route, min_route_length=4)

            ## sample random nodes
            # nodes = random.sample(graph.nodes, 2)
            # route = get_route(self.graph, nodes[0], nodes[1], amount)

            self.transfer(amount, route)

        self.num_steps += 1
        return self.get_state()

    def create_agent_node(self):
        """
        Add new node to the graph
        :return: The public key of the new node
        """
        # TODO [to Daniel] generate a random string (or hash of something) of the same size as the public keys.
        pub_key = len(self.graph.nodes) + 1
        self.graph.add_node(pub_key)
        return pub_key

    def add_edge(self, public_key_node1, public_key_node2, node1_balance, node2_balance):
        """

        :param public_key_node1:
        :param public_key_node2:
        :param node1_balance:
        :param node2_balance:
        :return:
        """
        capacity = node1_balance + node2_balance

        self.graph.add_edge(public_key_node1, public_key_node2, capacity=capacity,
                            node1_balance=node1_balance, node2_balance=node2_balance)

    def get_node_balance(self, node1_pub_key):
        connected_edges = self.graph.edges(nbunch=node1_pub_key, data=True)
        return 1  # TODO return the actual balance


    # TODO Structure of the json lightning node

    # {'channel_id': '666796627747143680',
    #  'chan_point': '73f0db04f86ffb58a13f6dcd5304c1a07b09a12d94e68b7ea2f7d735b010faf1:0',
    #  'last_update': 1589321706,
    #  'node1_pub': '033d8656219478701227199cbd6f670335c8d408a92ae88b962c49d4dc0e83e025',
    #  'node2_pub': '03abf6f44c355dec0d5aa155bdbdd6e0c8fefe318eff402de65c6eb2e1be55dc3e',
    #  'capacity': 16777215,
    #  'node1_policy': {'time_lock_delta': 40,
    #                   'min_htlc': 1000,
    #                   'fee_base_msat': 1000,
    #                   'fee_rate_milli_msat': 1,
    #                   'disabled': False,
    #                   'max_htlc_msat': '16609443000',
    #                   'last_update': 1589321706},
    #  'node2_policy': {'time_lock_delta': 30,
    #                   'min_htlc': 1000,
    #                   'fee_base_msat': 1000,
    #                   'fee_rate_milli_msat': 2500,
    #                   'disabled': False,
    #                   'max_htlc_msat': '16609443000',
    #                   'last_update': 1589289367},
    #  'node1_balance': 9991901.48150539,
    #  'node2_balance': 6785313.518494611,
    #  'betweenness': 0.05357142857142857}

#
# def initialize_graph(type: str) -> nx.Graph:
#     pass
