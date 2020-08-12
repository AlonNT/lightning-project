from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY
from routing.LND_routing import get_route
from collections import defaultdict

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


def grouped(iterable, number_to_group):
    """

    :param iterable: iterable
    :param number_to_group:
    :return:
    """
    # In case number_to_group = n we group every n elements
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
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
            # todo the amount is ok?
            # Get the path from node1 to node2 according the lnd_routing algorithm
            route = get_route(graph, src, dest, BETWEENNESS_TRANSFER_AMOUNT)

            # No route was found transferring 'amount; from 'source' to 'target'.
            # or the length of the route is short and its not interesting us
            if route is None or len(route) < 2:
                continue

            # Traverse the edges in the path in gruop of 2 (i.e every iteration takes two adjacent edges)
            for edge1_data, edge2_data in grouped(route, number_to_group=2):
                node1_edge1, node2_edge1, channel_id_edge1 = (edge1_data[0], edge1_data[1], edge1_data[2])
                node1_edge2, node2_edge2, channel_id_edge2 = (edge2_data[0], edge2_data[1], edge2_data[2])

                # Voting for group of two edges in the route, saving
                # TODO cant save dict as a key (graph.edges((edge1_data[0], edge1_data[1], edge1_data[2])),
                # TODO saving tuple of 6 elements - maybe there is a smarter way? type?
                participated_edges_counter[(node1_edge1, node2_edge1, channel_id_edge1,
                                            node1_edge2, node2_edge2, channel_id_edge2)] += 1

    # Sort the dictionary according to the values (i.e group of two edges that have passed through the mose
    # time are at the start/end according the minimize indicator)
    sorted_participated_edges_counter = sorted(participated_edges_counter.items(), key=lambda item: item[1],
                                               reverse=(not minimize))

    for edges_data, _ in sorted_participated_edges_counter:
        # Taking the start node in the first edge and the end of the second edge.
        # This is for connecting for both of this nodes
        node1_edge1 = edges_data[0]
        node2_edge2 = edges_data[4]
        for node in [node1_edge1, node2_edge2]:
            ordered_nodes_with_maximal_routeness.append(node)

    return ordered_nodes_with_maximal_routeness


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int, minimize=False, use_node_degree=False,
                 use_node_routeness=False):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds, channel_cost)
        self.default_balance_amount = initial_funds / 10

        self.minimize = minimize
        self.use_node_degree = use_node_degree
        self.use_node_routeness = use_node_routeness

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
            ordered_nodes = find_nodes_routeness(graph, self.minimize)
        else:
            ordered_nodes = find_minimize_channel_nodes(graph, self.minimize)

        # Choose the connected nodes to channel with minimal capcity until the initial_funds is over
        for other_node in ordered_nodes:
            # check if there are enough funds to establish a channel
            if funds_to_spend < self.channel_cost:
                break
            chanel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
            funds_to_spend -= self.channel_cost + chanel_balance
            # Create the channel details for the simulator
            # The other node's policy is determined by the simulator.
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': chanel_balance,
                               'node2_balance': chanel_balance}

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
