from typing import Tuple

MIN_BASE_FEE = 1e-6
MIN_PROPORTIONAL_FEE = 1e-6


class Channel:

    def __init__(self, nodes, balances: Tuple[float, float],
                 base_fee: int = MIN_BASE_FEE, proportional_fee: int = MIN_PROPORTIONAL_FEE, delay: float = None):
        """
        Initialize the channel with the balances and the two nodes in each side of the channel.
        Note that the capacity of the channel is the sum of the two balances.

        :param nodes: A tuple of two bytes-arrays - each is the address of the corresponding node.
        :param balances: A tuple of two integers - each is the balance of the corresponding node in this channel.
        :param base_fee: The base fee of this channel. Each transfer of funds through this channel
                         pays this fee, in addition to the proportional fee (see below).
        :param proportional_fee: The proportional fee of this channel - it's multiplied by the transaction's amount.
        """
        self.nodes = nodes

        # balances[0], balances[1] represent the balance on the left side and the right side respectively.
        self.balances: Tuple[float, float] = balances
        self.proportional_fee: int = proportional_fee
        self.base_fee: int = base_fee

        # TODO Check if we need it
        self.delay: float = delay

    @staticmethod
    def destroy_channel(channel):
        """

        :param channel:
        :return:
        """
        # TODO save this method in case we want to keep channels list in each node
        channel.nodes[0].channels.remove(channel)
        channel.nodes[1].channels.remove(channel)

    def update_fees(self, base_fee: int, proportional_fee: int):
        """
        Update the fees for the channel.

        :param base_fee: The new base fee.
        :param proportional_fee: The new proportional fee.
        """
        self.proportional_fee: int = proportional_fee
        self.base_fee: int = base_fee

    def transfer(self, amount: int):
        """"""
        self.balances[0] -= amount
        self.balances[1] += amount
        self.calculate_node_reward(amount)

    def can_transfer(self, amount: int) -> bool:
        # There is not enough money on this channel
        if self.balances[0] < amount:
            return False

        # self.nodes[1].receive() # todo change the bytes to actual nodes?? check this!!
        return True

    def other_node(self, node):
        return self.nodes[1] if self.nodes[0] == node else self.nodes[0]

    def calculate_node_reward(self, amount: int):
        """
        This function updates the reward of the two nodes that are involve in money transfer
        :return:
        """

        # TODO need to calculate the fee according algorithms !!!!
        fee_reward: int = self.base_fee + (self.proportional_fee * amount)

        # Updates the nodes with their reward for transfer the money through their channel

        # TODO there are two options for splitting the fee. Choose one of them!!!!!!!!

        # Option 1: 50-50
        self.update_nodes_reward(fee_reward/2, fee_reward/2)

        # Option 2: relative to the current state of the channel
        total_balance: int = self.balances[0] + self.balances[1]
        node1_fraction: int = self.balances[0] / total_balance
        node2_fraction: int = 1 - node1_fraction

        # TODO - Do we need to add the fee_reward to this calculation (i.e fee_reward_node1 + fee_reward)?
        fee_reward_node1: int = amount * node1_fraction + fee_reward
        fee_reward_node2: int = amount * node2_fraction + fee_reward

        self.update_nodes_reward(fee_reward_node1, fee_reward_node2)

    def update_nodes_reward(self, node1_reward: int, node2_reward: int):
        self.nodes[0].update_reward(node1_reward)
        self.nodes[1].update_reward(node2_reward)

    def __repr__(self):
        return f'channel: {self.nodes[0]}->{self.nodes[1]}'

    # TODO more functions (as we draw in the API).
