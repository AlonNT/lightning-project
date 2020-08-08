from Agents.AbstractAgent import AbstractAgent
from Agents.consts import DEFAULT_INITIAL_FUNDS
from garbage.consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY


def find_minimal_capacity_channel_nodes(graph, minimal_capacity: bool):
    """
    Finds nodes with minimal capacity
    :param graph: lightning graph
    :return: list of nodes that the agent want to connect to according to the minimal capacity of their channels
    """
    nodes_to_connect = list()
    # Use the nodes set for supervise which node we already chose.
    # if the node is already in this set we won't choose it again
    nodes_set = set()
    # Each item in this list contains capacity of the channel and the nodes that connected to this channel
    edge_keys_to_score = []

    # Traverse all the edges in the graph and append the edge capacity with the relevant nodes
    for n1, n2, edge_data in graph.edges(data=True):
        edge_keys_to_score.append([(edge_data['capacity'], [n1, n2])])
    # Sort the edges according to the capacity - maximal/minimal capacity
    if minimal_capacity:
        edge_keys_to_score = sorted(edge_keys_to_score)
    else:
        edge_keys_to_score = reversed(sorted(edge_keys_to_score))

    for capacity, edge_nodes in edge_keys_to_score:
        # Add the nodes to the list if they are not inside already
        for node in edge_nodes:
            if node not in nodes_set:
                nodes_to_connect.append(node)
                nodes_set.add(node)

    return nodes_to_connect


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS,  **kwargs):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 6

        # Boolean indicator To choose which strategy to choose (i.e maximal or minimal capacity)
        self.minimal_capacity = kwargs['capacity_strategy']

    def get_channels(self, graph):
        channels = list()
        funds_to_spend = self.initial_funds
        other_node_index: int = 0
        ordered_nodes = find_minimal_capacity_channel_nodes(graph, self.minimal_capacity)

        # Choose the connected nodes to channel with minimal capcity until the initial_funds is over
        while other_node_index < len(ordered_nodes):

            # Select the next node that the agent will connect to
            other_node = ordered_nodes[other_node_index]

            # Increase the index of the next node to connect to
            other_node_index += 1
            p = 0.5
            funds_to_spend -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            if funds_to_spend < 0:
                break
            # Create the channel details for the simulator
            # The other node's policy is determined by the simulator.
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': p * self.default_channel_capacity,
                               'node2_balance': (1 - p) * self.default_channel_capacity}

            channels.append(channel_details)

        return channels

    @property
    def name(self) -> str:
        return self.__class__.__name__
