import networkx as nx
from typing import List
from routing.route_selection import get_route


class Manager:
    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph

    def transfer(self, amount: int, src, dst) -> bool:
        """
        Preform transformation of money between two nodes
        :param amount: amount to transfer
        :param src:
        :param dst:
        :return:
        """
        # TODO - Daniel needs to check the direction for each node (for fees update).
        # TODO Gets (src,dst,channel_id) and needs to check which one is src for updating the fee

        # Gets the path from src to dst according the routing algorithm
        channels_path = self.get_channel_by_id(get_route(self.graph, src, dst))

        # Gets the total fee for this path
        total_fee: int = 0
        fees_list: List[int] = list()

        # Track the fees in each channel
        for i, channel in enumerate(channels_path):
            # TODO - check if the calculation is valid
            channel_fee = (channel["node1_base_fee"] + (channel["node1_proptional_fee"] * amount))
            total_fee += channel_fee
            fees_list[i] = channel_fee

        # Transformation on the first channel is the total fees of the fees
        fees_list.insert(0, 0)

        # Traverse the channels and check if the amount can pass through them.
        # In case the amount is valid to transfer, update the balances of the channels
        for i, channel in enumerate(channels_path):
            if channel["node1_balance"] < amount + total_fee - fees_list[i]:
                return False

        for i, channel in enumerate(channels_path):

            total_amount = amount + total_fee - fees_list[i]

            # Channel Updates
            channel["node1_balance"] -= total_amount
            channel["node2_balance"] += total_amount

        return True

    def get_state(self):
        return self.graph

    def step(self, action) -> nx.Graph:
        """
        This function gets an action from the agent and preform a step
        :param action: action from the agent
        :return: The current Graph
        """
        if action[0] == "add_edge":
            self.add_edge(*action[1])

        elif action[0] == "NOOP":
            pass
        else:
            raise ValueError(f"{action} not supported ")

        return self.graph

    def create_agent_node(self):
        """
        Add new node to the graph
        :return: The public key of the new node
        """
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

        self.graph.add_edge(public_key_node1, public_key_node2, capcity=capacity,
                            node1_balance=node1_balance, node2_balance=node2_balance)

    def get_node_balance(self, node1_pub_key):
        connected_edges = self.graph.edges(nbunch=node1_pub_key, data=True)
        return 1

    def get_channel_by_id(self, channels_id_list):
        """
        Gets list of channel id's and return the actual channels objects
        :param channels_id_list:
        :return:
        """
        channels_list = list()
        for channel_id in channels_id_list:
            channels_list.append(self.graph.edges(channel_id))
        return channels_list

#
# def initialize_graph(type: str) -> nx.Graph:
#     pass
