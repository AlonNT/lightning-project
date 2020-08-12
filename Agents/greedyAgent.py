from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY
from routing.LND_routing import get_route

BETWEENNESS_TRANSFER_AMOUNT = 10 ** 2


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
    :param graph: lightning graph
    :return: list with nodes according to their degree from high to low
    """
    nodes_to_connect = list()
    # List that contain the degree of each node in the network with its public key
    nodes_degree_data = list()

    # Traverse the nodes in the network and add for each node its degree
    for node in graph.nodes(data=True):
        nodes_degree_data.append((graph.degree[node[0]], node[0]))
    if minimize:
        nodes_degree_data = sorted(nodes_degree_data)
    else:
        nodes_degree_data = reversed(sorted(nodes_degree_data))

    # Create a list with nodes according to their degree from high to low
    for node_data in nodes_degree_data:
        nodes_to_connect.append(node_data[1])
    return nodes_to_connect


# TODO daniel count tuples of edges and vote for them (save a dict with tuple of edges (e1,e2) and vote
# TODO for them
def find_nodes_betweenness(graph, minimize: bool):
    """
    This function traverse all the paths between node to each other (according to lnd_routing algorithm) and
    counts the number of times a particular node appeared in the shortest path between two nodes in the graph
    :param graph: lightning graph
    :param minimize: boolean indicator To choose which strategy to choose (i.e maximal or minimal betweenness)
    :return: list of nodes that have the maximal betweenness
    (i.e nodes that participated in the maximum number of shortest path).
    """
    number_of_nodes = graph.number_of_nodes()

    # Betweenness centrality of a node scales with the number of pairs of nodes as suggested by the summation indices.
    # Therefore, the calculation may be rescaled by dividing through by the number of pairs of nodes.
    # todo maybe for lightning++
    normalization_factor_undirected_graph = ((number_of_nodes - 1) * (number_of_nodes - 2)) / 2

    # Create a dictionary for all nodes in the graph with a counter that indicate how many short-paths pass through them
    nodes_betweenness_counter = {node: 0 for node in graph.nodes()}
    # Nodes with maximal betweenness ordered
    ordered_nodes_with_maximal_betweenness = list()

    # Traverse all the routes between the nodes in the graph (O(N^2)), and getting the route according the lnd_routing
    for src in graph.nodes():
        for dest in graph.nodes():
            # todo ask about the amount
            # Get the path from node1 to node2 according the lnd_routing algorithm
            route = get_route(graph, src, dest, BETWEENNESS_TRANSFER_AMOUNT)

            # No route was found transferring 'amount; from 'source' to 'target'
            if route is None:
                continue
            # Traverse the nodes in the path and increase the nodes that participate in the route
            for node_path in route:
                first_node, second_node = node_path[0], node_path[1]
                # todo consult with alon and ariel about the nodes we want to
                nodes_betweenness_counter[second_node] += 1

    # Sort the dictionary according to the values (i.e nodes that have passed through them the most short paths will
    # be at the start) and append the public key of the 'best betweenness nodes' to ordered list
    nodes_betweenness_counter_sorted_by_value = sorted(nodes_betweenness_counter.items(), key=lambda item: item[1],
                                                       reverse=minimize)
    for key, _ in nodes_betweenness_counter_sorted_by_value:
        ordered_nodes_with_maximal_betweenness.append(key)

    return ordered_nodes_with_maximal_betweenness


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int, minimize=False, use_node_degree=False,
                 use_node_betweenness=False):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds, channel_cost)
        self.default_balance_amount = initial_funds / 10

        self.minimize = minimize
        self.use_node_degree = use_node_degree
        self.use_node_betweenness = use_node_betweenness

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
        elif self.use_node_betweenness:
            ordered_nodes = find_nodes_betweenness(graph, self.minimize)
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
            name += "-node_degree"
        elif self.use_node_betweenness:
            name += "-node_betweenness"
        else:
            name += "-node_capacity"

        return name
