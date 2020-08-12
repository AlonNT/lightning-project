from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY
from routing.LND_routing import get_route
from collections import defaultdict
from typing import NewType

ROUTENESS_TRANSFER_AMOUNT = 10 ** 2
# TODO Daniel?
GroupOfTwoEdgesKey = NewType('GroupOfTwoEdgesKey', ())


def find_minimize_channel_nodes(graph, minimize: bool):
    """
    Finds nodes with minimal/maximal capacity
    :param graph: lightning graph
    :param minimize: boolean indicator To choose which strategy to choose (i.e maximal or minimal capacity)
    :return: list of nodes that the agent want to connect to according to the minimal/maxima; capacity of their channels
    """
    nodes_to_connect = list()
    # Use the nodes set for supervise which node we already chose.
    # if the node is already in this set we won't choose it again
    nodes_set = set()
    # Each item in this list contains capacity of the channel and the nodes that connected to this channel
    edge_keys_to_score = list()

    # Traverse all the edges in the graph and append the edge capacity with the relevant nodes
    for n1, n2, edge_data in graph.edges(data=True):
        edge_keys_to_score.append((edge_data['capacity'], [n1, n2]))
    # Sort the edges according to the capacity - maximal/minimal capacity
    if minimize:
        edge_keys_to_score = sorted(edge_keys_to_score)
    else:
        edge_keys_to_score = reversed(sorted(edge_keys_to_score))

    for capacity, edge_nodes in edge_keys_to_score:
        # capacity, edge_nodes = item[0], item[1]
        # Add the nodes to the list if they are not inside already
        for node in edge_nodes:
            if node not in nodes_set:
                nodes_to_connect.append(node)
                nodes_set.add(node)

    return nodes_to_connect


def find_nodes_degree(graph, minimize: bool):
    """
    :param minimize: boolean indicator To choose which strategy to choose (i.e maximal or minimal degree)
    :param graph: lightning graph
    :return: list with nodes according to their degree from high to low
    """

    # Calculate the degree of all nodes in the lightning graph
    nodes_degree = list(graph.degree())
    if minimize:
        nodes_degree = sorted(nodes_degree, key=lambda item: item[1], reverse=(not minimize))
    else:
        nodes_degree = sorted(nodes_degree, key=lambda item: item[1], reverse=minimize)

    # Create a list with nodes according to their degree from high to low according to minimize indicator
    nodes_to_connect = [node_data[0] for node_data in nodes_degree]
    return nodes_to_connect


def grouped(iterable, number_to_group):
    """
    Take an iterable object and group it's items to 'number_to_group'.
    For example:
        Example 1:
            Input: [1,2,3,4,5,6], number_to_group=2
            Output: [(1,2), (3,4), (5,6)]

    :param iterable: iterable object
    :param number_to_group: number to group the items in the iterable object.
    :return: list of the grouped items in the iterable object.
    """

    return zip(*[iter(iterable)] * number_to_group)


def find_nodes_routeness(graph, minimize: bool):
    """
    This function traverse all the paths between node to each other (according to lnd_routing algorithm) and
    counts the number of times a group of two edges appeared in the shortest path between two nodes in the graph.
    Than, takes the nodes that  were on the start/end of the first_edge/second_edge accordingly
    :param graph: lightning graph
    :param minimize: boolean indicator To choose which strategy to choose (i.e maximal or minimal betweenness)
    :return: list of nodes that have the maximal betweenness
    (i.e nodes that participated in the maximum number of shortest path).
    """

    # Create a dictionary that the key are group of two edges in the graph with a counter that
    # indicate how many short-paths pass through them (according to lnd protocol)
    participated_edges_counter = defaultdict(lambda: 0)
    # Nodes that participate in the maximal routeness, in an order way
    ordered_nodes_with_maximal_routeness = list()

    # Traverse all the routes between the nodes in the graph (O(N^2)), and getting the route according the lnd_routing
    for src in graph.nodes():
        for dest in graph.nodes():
            # TODO the amount is ok?
            # Get the path from node1 to node2 according the lnd_routing algorithm
            route = get_route(graph, src, dest, ROUTENESS_TRANSFER_AMOUNT)

            # No route was found transferring 'amount; from 'source' to 'target',
            # or the length of the route is short and its not interesting us
            if route is None or len(route) < 2:
                continue

            # Traverse the edges in the path in group of 2 (i.e every iteration takes two adjacent edges)
            for edge1_data, edge2_data in grouped(route, number_to_group=2):
                node1_edge1, node2_edge1, channel_id_edge1 = (edge1_data[0], edge1_data[1], edge1_data[2])
                node1_edge2, node2_edge2, channel_id_edge2 = (edge2_data[0], edge2_data[1], edge2_data[2])

                # Voting for group of two edges in the route (without an order)
                # The keys are set because the order of the vertices does not matter in an undirected graph.
                # edge like this a-->b identical to b-->a
                key_edge1_data = (channel_id_edge1, frozenset([node1_edge1, node2_edge1]))
                key_edge2_data = (channel_id_edge2, frozenset([node1_edge2, node2_edge2]))
                key = frozenset([key_edge1_data, key_edge2_data])
                participated_edges_counter[key] += 1

    # Sort the dictionary according to the values (i.e group of two edges that have passed through the mose
    # time are at the start/end according the minimize indicator)
    sorted_participated_edges_counter = sorted(participated_edges_counter.items(), key=lambda item: item[1],
                                               reverse=(not minimize))
    # For avoiding nodes repetition
    nodes_set = set()

    # Combined the nodes in the edges (every couple of edges contain 3 nodes)
    for edges_data, _ in sorted_participated_edges_counter:

        # Get the nodes that participate in the edges and combined them to one list
        nodes_in_edges = [list(second) for first, second in edges_data]
        nodes_in_edges_combined = [node for item in nodes_in_edges for node in item]

        # Remove middle node, the agent will connect to the ends nodes
        ends_nodes_in_edges = [node for node in nodes_in_edges_combined if nodes_in_edges_combined.count(node) == 1]

        # Append the nodes that the greedy agent want to connect to
        for node in ends_nodes_in_edges:
            if node not in nodes_set:
                ordered_nodes_with_maximal_routeness.append(node)
                nodes_set.add(node)

    return ordered_nodes_with_maximal_routeness, sorted_participated_edges_counter


def get_edges_details(sorted_participated_edges_counter):
    """

    :param participated_edges_counter:
    :return:
    """
    # TODO Daniel - there is a bug here
    edges_details = list()
    for edges_data, _ in sorted_participated_edges_counter:
        # Get the nodes that participate in the edges and combined them to one list + the channel id
        edge_data = [edge for edge in edges_data]

        edge_details = [node for node in list(edge_data[1])]
        edge_details.append(edge_details[0])
        edges_details.append(edge_details)

    return edges_details


def calculate_agent_policy(graph, node):
    """
    Calculate the agent policy
    :param graph: lightning graph
    :param node: tuple of the edge data (node1, node2, channel_data)
    :return: min_time_lock_delta, min_base_fee, min_proportional_fee for the agent policy
    """

    # TODO maybe not take the minimal our of these?
    min_base_fee = float('inf')
    min_proportional_fee = float('inf')
    min_time_lock_delta = float('inf')

    for node1, node2, channel_data in graph.edges(node, data=True):
        node_i = 1 if node == channel_data['node1_pub'] else 2
        node_policy = channel_data[f'node{node_i}_policy']

        # TODO are there more values to take into account?
        base_fee = node_policy['fee_base_msat']
        proportional_fee = node_policy['proportional_fee']
        time_lock_delta = node_policy['time_lock_delta']

        min_base_fee = min(min_base_fee, base_fee)
        min_proportional_fee = min(min_proportional_fee, proportional_fee)
        min_time_lock_delta = min(min_time_lock_delta, time_lock_delta)

    return min_time_lock_delta, min_base_fee, min_proportional_fee


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int, minimize=False, use_node_degree=False,
                 use_node_routeness=False):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds, channel_cost)

        self.default_balance_amount = initial_funds / 10

        self.minimize = minimize
        self.use_node_degree = use_node_degree
        self.use_node_routeness = use_node_routeness

    def get_channels_in_routeness_use(self, sorted_participated_edges_counter, ordered_nodes, funds_to_spend, graph):
        """

        :param graph:
        :param participated_edges_counter:
        :param ordered_nodes:
        :param funds_to_spend:
        :return:
        """
        channels = list()

        edges_details = get_edges_details(sorted_participated_edges_counter)
        for edge_details in edges_details:
            min_time_lock_delta, min_base_fee, min_proportional_fee = calculate_agent_policy(graph,
                                                                                             edge_details)
            # Choose the connected nodes to channel with minimal capcity until the initial_funds is over
            for node_to_connect in ordered_nodes:
                # check if there are enough funds to establish a channel
                if funds_to_spend < self.channel_cost:
                    break
                channel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
                funds_to_spend -= self.channel_cost + channel_balance

                channel_details = {'node1_pub': self.pub_key, 'node2_pub': node_to_connect,
                                   'node1_policy': {"time_lock_delta": min_time_lock_delta,
                                                    "fee_base_msat": min_base_fee,
                                                    "proportional_fee": min_proportional_fee},
                                   'node1_balance': channel_balance,
                                   'node2_balance': channel_balance}
                channels.append(channel_details)
        return channels

    def get_channels(self, graph):
        """
        This function create channels details according to the agent strategy, This agent can choose the vertices with
        which he wants to connect according to different strategies:
            (1) Nodes with maximal/minimal capacity (their balances in all the channels)
            (2) Nodes with the maximal/minimal degree (i.e have the most/lowest channels in the network)
            (3) Nodes with the maximal/minimal betweenness
        :param graph: lightning graph
        :return: List with channels details (i.e the nodes that opened the channel, balances and policy)
        """
        channels = list()
        funds_to_spend = self.initial_funds

        # Choose between the strategies
        if self.use_node_degree:
            ordered_nodes = find_nodes_degree(graph, self.minimize)
        elif self.use_node_routeness:
            ordered_nodes, sorted_participated_edges_counter = find_nodes_routeness(graph, self.minimize)
            return self.get_channels_in_routeness_use(sorted_participated_edges_counter, ordered_nodes,
                                                      funds_to_spend, graph)
        else:
            ordered_nodes = find_minimize_channel_nodes(graph, self.minimize)

        # Choose the connected nodes to channel with minimal capcity until the initial_funds is over
        for other_node in ordered_nodes:
            # check if there are enough funds to establish a channel
            if funds_to_spend < self.channel_cost:
                break
            channel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
            funds_to_spend -= self.channel_cost + channel_balance

            # Create the channel details for the simulator
            # The other node's policy is determined by the simulator.
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': channel_balance,
                               'node2_balance': channel_balance}

            channels.append(channel_details)

        return channels

    @property
    def name(self) -> str:
        name = self.__class__.__name__

        if self.minimize:
            name += "-minimal"
        else:
            name += "-maximal"

        if self.use_node_degree:
            name += "-node_routeness"
        elif self.use_node_routeness:
            name += "-node_routeness"
        else:
            name += "-node_capacity"

        return name
