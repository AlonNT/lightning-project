from typing import List
import channel
import networkx as nx


class Node:

    def __init__(self, address: str, graph: nx.Graph = None, channels: channel.Channel = None):

        #todo change the type of address to bytes when working with lightning network
        self.address: str = address
        self.graph: nx.Graph = graph
        self.reward = 0

        # TODO Do we need it?
        self.channels: channel.Channel = channels if not channels else []

    def get_address(self):
        """
        :return: The address of this node on the lightning network
        """
        return self.address


    def send(self, address: bytes, amount: int) -> bool:
        # TODO - assume that we get a list of edges from the routing algorithm (for the miniml path to address)
        channel_path : List[channel.Channel] = self.route(address)

        # Traverse the channels and check if the amount can pass through them.
        # In case the amount is Okay to transfer, update the balances of the channels
        for channel in channel_path:
            if not channel.can_transfer(amount=amount):
                return False

        # Update Balances
        for channel in channel_path: channel.transfer(amount)

        return True

    def update_reward(self, fee_reward: int):
        self.reward += fee_reward

    def receive(self) -> bool:
        # TODO do we need it?
        pass

    def route(self, address: bytes) -> List[channel.Channel]:
        # TODO alon
        pass

    def __repr__(self):
        return f'Node{self.address}'





