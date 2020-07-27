import random
import networkx as nx
from Agents import AbstractAgent
from consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY

# todo delete this after pulling the changes
DEFAULT_INITIAL_FUNDS = 5


class RandomInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS):
        super(AbstractAgent).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 6

    def get_channels(self, graph: nx.MultiGraph):
        funds_to_spend = self.initial_funds
        channels = list()
        while funds_to_spend > 0:
            random_node_pub_key = random.choice([node for node in graph.nodes if node.public_key != self.public_key])
            p = random.random()
            funds_to_spend -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            if funds_to_spend < 0:
                break
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': random_node_pub_key,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': p * self.default_channel_capacity,
                               'node2_balance_2': (1 - p) * self.default_channel_capacity}
            channels.append(channel_details)

        assert (len(channels) == 0, "Channels list is empty")
        return channels

        # TODO use this if we want to work with steps
        # def act(self, graph):
        #     if self.added_edges < self.max_edges and random.random() < 0.3:
        #         random_node_pub_key = random.choice(list(graph.nodes))
        #         while random_node_pub_key == self.public_key:
        #             random_node_pub_key = random.choice(list(graph.nodes))
        #         p = random.random()
        #         self.balance -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
        #         command_arguments = {'node1_pub': self.public_key, 'node2_pub': random_node_pub_key,
        #                              'node1_policy': LND_DEFAULT_POLICY,
        #                              'node1_balance': p * self.default_channel_capacity,
        #                              'node2_balance_2': (1 - p) * self.default_channel_capacity}
        #         self.added_edges += 1
        #         return 'add_edge', list(command_arguments.values())
        #     else:
        #         return 'NOOP', {}
