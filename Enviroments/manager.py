import networkx as nx
from typing import List
from routing.naive_routing import get_route


def get_src_dst_nodes_on_channel(src):
    source_i = 1 if src == "node1_pub" else 2
    target_i = 1 + (2 - source_i)  # if source_i is 1 it's 1+(2-1)=2, if source_i is 2 it's 1+(2-2)=1.

    return f'node{source_i}_balance', f'node{target_i}_balance'


def get_channel_fee_according_to_src(src, channel, amount: int):
    """
    :param node:
    :return: return the channel fee that corresponds to src node
    """
    # Gets the policy of source node and calculate the fee according to the channel
    policy_key = "node1_policy" if src == "node1_pub" else "node2_policy"
    return channel[policy_key]["fee_base_msat"] + (amount * channel[policy_key]["fee_rate_milli_msat"])


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
        # TODO Gets (src,dst,channel_id) and needs to check which one is src for updating the fee - FIX

        # Gets the path and nodes order in the channel (src, dst) according the routing algorithm
        channels_path, nodes_order_by_channel = self.get_channel_by_id(get_route(self.graph, src, dst), src)

        # Gets the total fee for this path
        total_fee: int = 0
        fees_list: List[int] = list()

        # Track the fees in each channel
        for i, channel in enumerate(channels_path):
            # TODO - check if the calculation is valid
            channel_fee = get_channel_fee_according_to_src(nodes_order_by_channel[i], channel, amount)
            total_fee += channel_fee
            fees_list[i] = channel_fee

        # Transformation of the first channel is the total fees
        fees_list.insert(0, 0)

        # Traverse the channels and check if the amount can pass through them.
        # In case the amount is valid to transfer, update the balances of the channels
        for i, channel in enumerate(channels_path):
            src_node_balance, dst_node_balance = get_src_dst_nodes_on_channel(nodes_order_by_channel[i])
            # TODO [to Daniel] I think this calculation is wrong - you need to take into account the fact that
            # TODO [to Daniel] there are already paid fee. So you don't need to subtract always 'total_fee'
            # TODO [to Daniel] from the amount, but you need to subtract a fee that is decreasing
            # TODO [to Daniel] (more fees need to be 'carried' in the beginning of the path).
            if channel[src_node_balance] < amount + total_fee - fees_list[i]:
                return False

        for i, channel in enumerate(channels_path):

            total_amount = amount + total_fee - fees_list[i]

            # Gets the nodes order in this channel for updating the amount on their channel sides
            src_node_balance, dst_node_balance = get_src_dst_nodes_on_channel(nodes_order_by_channel[i])

            # Channel Updates
            channel[src_node_balance] -= total_amount
            channel[dst_node_balance] += total_amount

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

        if function_name == "add_edge":
            self.add_edge(*args)
        elif function_name == "NOOP":
            pass
        else:
            raise ValueError(f"{function_name} not supported ")

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

    def get_channel_by_id(self, channels_id_list, src_node):
        """
        Gets list of channel id's and return the actual channels objects
        :param channels_id_list: n'th of tuples that composed of 3 variables - (node1, node2, channel_id)
        :return:
        """
        channels_list = list()
        nodes_order_by_channel = list()
        temp_src = src_node
        for i, channel_id in enumerate(channels_id_list):
            # Channels_list[i] is a tuple of 3 variables - (node1, node2, channel_id)
            # TODO Check this - check attr names + nodes_address
            if channels_list[i][0] == temp_src:
                nodes_order_by_channel.append("node1_pub")
            else:
                nodes_order_by_channel.append("node2_pub")

            # src is the second node
            temp_src = channels_list[i][1]
            channels_list.append(self.graph.edges(channel_id))
        return channels_list, nodes_order_by_channel

    def get_channel_source(self, channel, src):
        # Get the source of the channel and check if that node is node1 or node2
        pass

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
