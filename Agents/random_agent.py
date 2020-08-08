import random
from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY
import networkx as nx


class RandomInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int):
        super(RandomInvestor, self).__init__(public_key, initial_funds, channel_cost)
        self.default_balance_amount = initial_funds / 10

    def get_channels(self, graph: nx.MultiGraph):
        funds_to_spend = self.initial_funds
        channels = list()
        while funds_to_spend >= self.channel_cost:
            random_node_pub_key = random.choice([node for node in graph.nodes if graph.nodes[node]['pub_key'] != self.pub_key])

            chanel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
            funds_to_spend -= self.channel_cost + chanel_balance

            channel_details = {'node1_pub': self.pub_key, 'node2_pub': random_node_pub_key,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': self.default_balance_amount,
                               'node2_balance': self.default_balance_amount}
            channels.append(channel_details)

        # assert len(channels) == 0, "Channels list is empty" # Why TF do we need this empty?
        return channels

    @property
    def name(self) -> str:
        return self.__class__.__name__
