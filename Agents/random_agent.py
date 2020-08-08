import random
import networkx as nx
from Agents.AbstractAgent import AbstractAgent
from consts import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY
from Agents.consts import DEFAULT_INITIAL_FUNDS


class RandomInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS):
        super(RandomInvestor, self).__init__(public_key, initial_funds)
        self.default_channel_capacity = 10 ** 5

    def get_channels(self, graph: nx.MultiGraph):
        funds_to_spend = self.initial_funds
        channels = list()
        while funds_to_spend > 0:
            random_node_pub_key = random.choice([node for node in graph.nodes if graph.nodes[node]['pub_key'] != self.pub_key])
            p = random.random()
            funds_to_spend -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            if funds_to_spend < 0:
                break
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': random_node_pub_key,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': p * self.default_channel_capacity,
                               'node2_balance': (1 - p) * self.default_channel_capacity}
            channels.append(channel_details)

        # assert len(channels) == 0, "Channels list is empty" # Why TF do we need this empty?
        return channels

    @property
    def name(self) -> str:
        return self.__class__.__name__
