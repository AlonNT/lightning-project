from Agents.AbstractAgent import AbstractAgent
from Agents.consts import DEFAULT_INITIAL_FUNDS
from garbage.consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY


def find_minimal_capacity_channel_nodes(graph):
    """
    Finds nodes with minimal capacity
    :param graph: lightning graph
    :return: list of nodes that the agent want to connect to according to the minimal capacity of their channels
    """
    nodes_to_connect = list()
    nodes_set = set()
    edge_keys_to_score = []

    # Traverse all the edges in the graph and append the edge capacity with the relevant nodes
    for n1, n2, edge_data in graph.edges(data=True):
        edge_keys_to_score.append([(edge_data['capacity'], [n1, n2])])

    # Sort the edges according to the capacity
    edge_keys_to_score = sorted(edge_keys_to_score)
    for nodes in edge_keys_to_score:

        # Add the nodes to the list if they are not inside already
        if nodes[1][0] not in nodes_set:
            nodes_to_connect.append(nodes[1][0])
            nodes_set.add(nodes[1][0])

        if nodes[1][1] not in nodes_set:
            nodes_to_connect.append(nodes[1][1])
            nodes_set.add(nodes[1][1])

    return nodes_to_connect


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 6

    def get_channels(self, graph):
        channels = list()
        funds_to_spend = self.initial_funds
        other_node_index: int = 0
        best_nodes_to_connect = find_minimal_capacity_channel_nodes(graph)
        while funds_to_spend > 0 and other_node_index < len(best_nodes_to_connect):
            other_node = best_nodes_to_connect[other_node_index]
            other_node_index += 1
            p = 0.5
            funds_to_spend -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': p * self.default_channel_capacity,
                               'node2_balance': (1 - p) * self.default_channel_capacity}

            channels.append(channel_details)

        # assert len(channels) == 0, "Channels list is empty" # Why TF do we need this empty?
        return channels

    @property
    def name(self) -> str:
        return self.__class__.__name__
