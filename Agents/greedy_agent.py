from consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY
from Agents.AbstractAgent import AbstractAgent
from Agents.consts import DEFAULT_INITIAL_FUNDS


def find_minimal_capacity_channel_nodes(graph, funds: int, public_key):
    """Finds nodes with minimal capacity"""
    nodes_set = set()
    edge_keys_to_score = []
    for n1, n2, edge_data in graph.edges(data=True):
        edge_keys_to_score += [(edge_data['capacity'], [n1, n2])]
    edge_keys_to_score = sorted(edge_keys_to_score)
    for item in edge_keys_to_score:
        # Added the nodes
        nodes_set.add(item[1][0])
        nodes_set.add(item[1][1])

    return list(nodes_set)


class GreedyNodeInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS):
        super(GreedyNodeInvestor, self).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 6

    def get_channels(self, graph):
        channels = list()
        funds_to_spend = self.initial_funds
        other_node_index: int = 0
        best_nodes = find_minimal_capacity_channel_nodes(graph, self.initial_funds, self.pub_key)
        while funds_to_spend > 0 and other_node_index < len(best_nodes):
            other_node = best_nodes[other_node_index]
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
