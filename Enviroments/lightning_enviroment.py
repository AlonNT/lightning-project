import random

import networkx as nx
import numpy as np

from consts import LND_DEFAULT_POLICY
from routing.LND_routing import get_route
from utils.common import calculate_route_fees, get_new_position_for_node
from utils.visualizers import visualize_graph_state
from utils.graph_helpers import sample_long_route

class LightningEniroment:
    """This object is an openAI-like enviroment: its internal state is the Lightning graph and it sumulates flow in
    it at each step.
    """

    def __init__(self, graph: nx.Graph, tranfers_per_step, transfer_max_amount, verbose=False):
        self.graph: nx.Graph = graph
        self.positions = nx.spring_layout(self.graph, seed=None)
        self.tranfers_per_step = tranfers_per_step
        self.transfer_max_amount = transfer_max_amount
        self.num_steps = 0
        self.agent_pub_key = None
        self.debug_last_transfer_trials = []
        self.verbose = verbose

    def get_state(self):
        """Returns the internal state of this enviroment"""
        return self.graph

    def step(self, action):
        """
        This function gets an action from the agent changes the internal state accordingly and returns the new state
        :param action: action from the agent a tuple containig (desired enviroment function, desired function arguments)
        :return: the new state
        """
        function_name, args = action
        if function_name == "add_edge":
            self._add_edge(*args)
        elif function_name == "NOOP":
            pass
        else:
            raise ValueError(f"{function_name} not supported ")

        for step in range(self.tranfers_per_step):
            amount = random.randint(self.transfer_max_amount - 1, self.transfer_max_amount)

            # # Sample long route for debugging
            # route, src, dest = sample_long_route(self.graph, amount, get_route, min_route_length=4)

            # sample random nodes
            choice_nodes = [node_pub_key for node_pub_key in self.graph.nodes if node_pub_key != self.agent_pub_key]
            nodes = random.sample(choice_nodes, 2)
            route = get_route(self.graph, nodes[0], nodes[1], amount)
            if route is not None:
                self._transfer(amount, route)

        self.num_steps += 1
        return self.get_state()

    def create_agent_node(self):
        """
        Add new node to the graph
        :return: The public key of the new node
        """
        serial_num = len(self.graph.nodes) + 1
        pub_key = "Agnent-" + str(serial_num)
        self.graph.add_node(pub_key, pub_key=pub_key, serial_number=serial_num)
        self.positions[pub_key] = get_new_position_for_node(self.positions)
        if self.agent_pub_key is not None:
            raise Warning("Enviroment currently supports one agent and one node addition")
        self.agent_pub_key = pub_key
        return pub_key

    def get_node_balance(self, node_pub_key):
        total_balance = 0
        connected_edges = self.graph.edges(node_pub_key, data=True)
        for _, _, edge_data in connected_edges:
            if node_pub_key == edge_data['node1_pub']:
                total_balance += edge_data['node1_balance']
            else:
                total_balance += edge_data['node2_balance']
        return total_balance

    def render(self, save_path=None, agent_balance=None):
        """
        Creates an image describing the current state togetehr with the trasfers made between last state and the
        current
        """
        visualize_graph_state(self.graph, self.positions, transfer_routes=self.debug_last_transfer_trials,
                              save_path=save_path,
                              verify_node_serial_number=False,
                              plot_title=f"step-{self.num_steps}",
                              additional_node_info={self.agent_pub_key: f"Agent balance: {agent_balance}"})
        self.debug_last_transfer_trials = []

    def _add_edge(self, node1_pub, node2_pub, node1_policy, node1_balance, node2_balance):
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
            print( f"\tManager | Adding edge between node({self.graph.nodes[node1_pub]['serial_number']})"
                   f" and node({self.graph.nodes[node2_pub]['serial_number']})")
        capacity = node1_balance + node2_balance
        channel_id = str(len(self.graph.edges) + 1)
        self.graph.add_edge(node1_pub, node2_pub, channel_id,  # This is ok for multigraphs
                            channel_id=channel_id, node1_pub=node1_pub, node2_pub=node2_pub,
                            node1_policy=node1_policy, node2_policy=LND_DEFAULT_POLICY,
                            capacity=capacity, node1_balance=node1_balance, node2_balance=node2_balance)
        # Todo : update node2 total capacity

    def _transfer(self, amount: int, route):
        """
        Preform transformation of money between two nodes
        :param amount: amount to transfer
        :param route: list of edges
        :return:
        """
        debug_src_serial_num = self.graph.nodes[route[0][0]]['serial_number']
        debug_dst_serial_num = self.graph.nodes[route[-1][1]]['serial_number']
        if self.verbose:
            print(f"\tManager | Trying to transfer {amount} "
                  f"mast from node({debug_src_serial_num}) to node({debug_dst_serial_num})")

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
                if self.verbose:
                    print(f"\tManager | Failed! not enough funds in node({self.graph.nodes[src]['serial_number']})"
                          f" ({src_node_balance} < {amount + cumulaive_fees[i]})")
                self.debug_last_transfer_trials += [(route[0][0], route[-1][1], route, i)]
                return

        for i, (src, dest, channel_id) in enumerate(route):
            edge_data = self.graph.edges[(src, dest, channel_id)]
            if edge_data['node1_pub'] == src:
                src_node_balance_name, dst_node_balance_name = 'node1_balance', 'node2_balance'
            else:
                src_node_balance_name, dst_node_balance_name = 'node2_balance', 'node1_balance'
            # Channel Updates
            edge_data[src_node_balance_name] -= amount + cumulaive_fees[i]
            edge_data[dst_node_balance_name] += amount + cumulaive_fees[i]

        if self.verbose:
            print("\tManager | Transferred!!")
        self.debug_last_transfer_trials += [(route[0][0], route[-1][1], route, len(route))]
