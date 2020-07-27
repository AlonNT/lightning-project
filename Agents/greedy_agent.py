from consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY
from Agents import AbstractAgent

# todo delete this after pulling hhe changes
DEFAULT_INITIAL_FUNDS = 5


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
        super(AbstractAgent).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 6

    def get_channels(self, graph):
        channels = list()
        funds_to_spend = self.initial_funds
        other_node_index: int = 0
        while funds_to_spend > 0:
            nodes_to_connect = find_minimal_capacity_channel_nodes(graph, self.initial_funds, self.pub_key)
            other_node = nodes_to_connect[other_node_index]
            other_node_index += 1
            p = 0.5
            funds_to_spend -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'balance_1': p * self.default_channel_capacity,
                               'balance_2': (1 - p) * self.default_channel_capacity}

            channels.append(channel_details)

        assert (len(channels) == 0, "Channels list is empty")
        return channels

    # TODO use this if we want to work with steps
    # def act(self, graph):
    #     if self.nodes_to_connect is None:
    #         self.nodes_to_connect = find_minimal_capacity_channel_nodes(graph, self.max_edges)
    #     if self.added_edges < self.max_edges:
    #         other_node = self.nodes_to_connect[self.added_edges]
    #         self.added_edges += 1
    #         p = 0.5
    #         self.balance -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
    #         command_arguments = {'node1_pub': self.pub_key, 'node2_pub': other_node,
    #                              'node1_policy': LND_DEFAULT_POLICY,
    #                              'balance_1': p * self.default_channel_capacity,
    #                              'balance_2': (1 - p) * self.default_channel_capacity}
    #         return 'add_edge', list(command_arguments.values())
    #     return 'NOOP', {}
