from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY


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


def find_nodes_with_maximal_degree(graph, minimize: bool):
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


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int, minimize=False, use_node_degree=False):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds, channel_cost)
        self.default_balance_amount = initial_funds / 10

        self.minimize = minimize
        self.use_node_degree = use_node_degree

    def get_channels(self, graph):
        channels = list()
        funds_to_spend = self.initial_funds
        if self.use_node_degree:
            ordered_nodes = find_nodes_with_maximal_degree(graph, self.minimize)
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

        # assert len(channels) == 0, "Channels list is empty" # Why TF do we need this empty?
        return channels

    @property
    def name(self) -> str:
        name =  self.__class__.__name__
        if self.minimize:
            name += "-minimal"
        else:
            name += "-maximal"
        if self.use_node_degree:
            name += "-node_degree"
        else:
            name += "-node_capacity"

        return name