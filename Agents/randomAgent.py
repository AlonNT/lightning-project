import random
from Agents.AbstractAgent import AbstractAgent
from utils.common import LND_DEFAULT_POLICY
import networkx as nx


class RandomInvestor(AbstractAgent):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int):
        super(RandomInvestor, self).__init__(public_key, initial_funds, channel_cost)
        self.default_balance_amount = initial_funds / 10

    def get_channels(self, graph: nx.MultiGraph):
        """
        This function create channels details according to the agent strategy, This agent can choose the vertices with
        which he wants to connect according to his random strategy:
            (1) Pick random node in the graph and establish connection with it

        :param graph: lightning graph
        :return: List with channels details (i.e the nodes that opened the channel, balances and policy)
        """
        funds_to_spend = self.initial_funds
        channels = list()
        while funds_to_spend >= self.channel_cost:
            # Check if there are enough funds to establish a channel
            if funds_to_spend < self.channel_cost:
                break
            # Choose random public_key for connection
            random_node_pub_key = random.choice([node for node in graph.nodes if graph.nodes[node]['pub_key'] != self.pub_key])

            # Randomize the balances
            chanel_balance = min(self.default_balance_amount, funds_to_spend - self.channel_cost)
            funds_to_spend -= self.channel_cost + chanel_balance

            # Create the channel details for the simulator
            # The other node's policy is determined by the simulator.
            channel_details = {'node1_pub': self.pub_key, 'node2_pub': random_node_pub_key,
                               'node1_policy': LND_DEFAULT_POLICY,
                               'node1_balance': chanel_balance}
            channels.append(channel_details)

        return channels

    @property
    def name(self) -> str:
        return self.__class__.__name__
