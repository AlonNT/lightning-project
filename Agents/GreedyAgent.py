from collections import defaultdict
from typing import NewType

from Agents.AbstractAgent import AbstractAgent
from routing.LND_routing import get_route
from utils.common import LND_DEFAULT_POLICY
from utils.common import calculate_agent_policy

# this number is used in the LND routing algorithm that is used to sort edges by their attractiveness for  transactions
# it is better to keep this number as close as possible to the amount that the simulator actually transfers

# TODO [Daniel] keep playing with this const for better results
ROUTENESS_TRANSFER_AMOUNT = 10 ** 2


def sort_nodes_by_channel_capacity(graph, minimize: bool):
    """
    Finds nodes with minimal/maximal capacity of the channles between them
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


def sort_nodes_by_degree(graph, minimize: bool):
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


def sort_nodes_by_routeness(graph, minimize: bool):
    """
    This function traverse all the paths between node to each other (according to lnd_routing algorithm) and
    counts the number of times a group of two edges appeared in the shortest path between two nodes in the graph.
    Than, takes the nodes that  were on the start/end of the first_edge/second_edge accordingly
    :param graph: lightning graph
    :param minimize: boolean indicator To choose which strategy to choose (i.e maximal or minimal betweenness)
    :return:
            (1) list of nodes that have the maximal betweenness
                (i.e nodes that participated in the maximum number of shortest path).
    """

    # Create a dictionary that the key are group of two edges in the graph with a counter that
    # indicate how many short-paths pass through them (according to lnd protocol)
    participated_edges_counter = defaultdict(lambda: 0)
    # Nodes that participate in the maximal routeness, in an order way
    ordered_nodes_with_maximal_routeness = list()

    # Traverse all routes between the nodes in the graph (O(N^2)*T(LND)), getting the route according the lnd_routing
    for src in graph.nodes():
        for dest in graph.nodes():
            if dest == src or dest in graph.neighbors(src):
                continue  # Early termination for cases where a two edges fastest route cannot exist

            # Get the path from node1 to node2 according the lnd_routing algorithm
            route = get_route(graph, src, dest, ROUTENESS_TRANSFER_AMOUNT)
            if route is None:
                continue  # No route was found transferring 'amount; from 'source' to 'target',
            assert len(route) > 1  # This should not happen: we verified no short route can exist

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
    nodes_rank = dict()
    # Combined the nodes in the edges (every couple of edges contain 3 nodes)
    for edges_data, _ in sorted_participated_edges_counter:

        # Get the nodes that participate in the edges and combined them to one list
        nodes_in_edges = [list(nodes) for channel_id, nodes in edges_data]  # Note the list cast from frozenset
        nodes_in_edges_combined = [node for nodes_list in nodes_in_edges for node in nodes_list]

        # Remove middle node, the agent will connect to the ends nodes (middle node is in both edges i.e count == 2)
        ends_nodes_in_edges = [node for node in nodes_in_edges_combined if nodes_in_edges_combined.count(node) == 1]

        # Append the nodes that the greedy agent want to connect to
        for node in ends_nodes_in_edges:
            if node not in nodes_set:
                ordered_nodes_with_maximal_routeness.append(node)
                nodes_set.add(node)

    return ordered_nodes_with_maximal_routeness, participated_edges_counter


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int,
                 minimize=False, use_node_degree=False, use_node_routeness=False, desired_num_edges=10):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds, channel_cost)

        self.minimize = minimize
        self.use_node_degree = use_node_degree
        self.use_node_routeness = use_node_routeness
        self.desired_num_edges = desired_num_edges
        self.default_balance_amount = initial_funds / self.desired_num_edges

    def get_channels(self, graph):
        """
        This function create channels details according to the agent strategy, This agent can choose the vertices with
        which he wants to connect according to different strategies:
            (1) Nodes in channels with maximal/minimal capacity
            (2) Nodes with the maximal/minimal degree (i.e have the most/lowest channels in the network)
            (3) Nodes with the maximal/minimal betweenness
        :param graph: lightning graph
        :return: List with channels details (i.e the nodes that opened the channel, balances and policy)
        """
        channels = list()
        funds_to_spend = self.initial_funds
        # Choose between the strategies
        if self.use_node_degree:
            ordered_nodes = sort_nodes_by_degree(graph, self.minimize)
        elif self.use_node_routeness:
            ordered_nodes, _ = sort_nodes_by_routeness(graph, self.minimize)
        else:
            ordered_nodes = sort_nodes_by_channel_capacity(graph, self.minimize)

        # Choose the connected nodes to channel with minimal capacity until the initial_funds is over
        for node_to_connect in ordered_nodes:

            # Check if there are enough funds to establish a channel
            if funds_to_spend < self.channel_cost:
                break

            channel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
            funds_to_spend -= self.channel_cost + channel_balance

            # Create the channel details for the simulator
            # The other node's policy is determined by the simulator.
            if self.use_node_routeness:
                min_time_lock_delta, min_base_fee, min_proportional_fee = calculate_agent_policy(graph,
                                                                                                 node=node_to_connect)
                agent_policy = {"time_lock_delta": min_time_lock_delta,
                                "fee_base_msat": min_base_fee,
                                "proportional_fee": min_proportional_fee}
            else:
                agent_policy = LND_DEFAULT_POLICY

            channel_details = {'node1_pub': self.pub_key, 'node2_pub': node_to_connect,
                               'node1_policy': agent_policy,
                               'node1_balance': channel_balance}

            channels.append(channel_details)

        return channels

    @property
    def name(self) -> str:
        name = "Greedy"

        if self.minimize:
            name += "-min"
        else:
            name += "-max"

        if self.use_node_degree:
            name += "-degree"
        elif self.use_node_routeness:
            name += "-routeness"
        else:
            name += "-capacity"
        name += f'(d={self.desired_num_edges})'
        return name
