from typing import List
from functools import lru_cache
MIN_BASE_FEE = 1e-6
MIN_PROPORTIONAL_FEE = 1e-6
MIN_DELAY = 4
INFINITY_INT = 999_999_999_999_999


# TODO [to Ariel] WTF is BGF?
class BFG:
    __slots__ = ('total', 'risk', 'prev', 'sum')

    def __init__(self, total=INFINITY_INT, risk=INFINITY_INT, prev=None):
        self.total = total
        self.risk = risk
        self.prev = prev
        self.sum = None

    def __repr__(self):
        return f'BFG prev={self.prev}, total={self.total}, risk={self.risk}'


class Node:
    __slots__ = ('name', 'channels', 'bfg', 'dijkstra_info')

    def __init__(self, channels=None, name=None):
        self.name = name
        self.channels = channels or []
        self.bfg: List[BFG] = []
        self.dijkstra_info = None

    def __repr__(self):
        return f'Node{self.name}'

    def __dict__(self):
        return {'name': self.name}


class Channel:
    __slots__ = ('node1', 'node2', 'base_fee', 'proportional_fee', 'delay', 'scid', 'capacity', 'height')
    max_height = 0

    # fees are in milli-satoshis,
    def __init__(self, node1: Node, node2: Node, base_fee: int, proportional_fee: float, delay: float,
                 scid: bytes = None, capacity: int = 0, height: int = 0):
        self.node1 = node1
        self.node2 = node2
        self.base_fee = base_fee
        self.proportional_fee = proportional_fee
        self.delay = delay
        self.scid = scid
        self.capacity = capacity  # in satoshis
        self.height = height  # number of blocks that this channel is up until now

    # TODO [to Ariel] WTF is lru_cache? Is it relates to the multi-processing shit?
    @lru_cache(maxsize=200000)
    def other_node(self, node) -> Node:
        return self.node1 if self.node2 == node else self.node2

    @lru_cache(maxsize=100000)
    def degree(self) -> int:
        return len(self.node1.channels) + len(self.node2.channels)

    # TODO No one uses the returned channel, so maybe we don't need to return it...
    @staticmethod
    def create_channel(node1: Node, node2: Node, base_fee: int = MIN_BASE_FEE,
                       proportional_fee: float = MIN_PROPORTIONAL_FEE, delay: float = MIN_DELAY,
                       scid: bytes = None, capacity: int = 0, height: int = 0):
        channel = Channel(node1, node2, base_fee, proportional_fee, delay, scid, capacity, height)
        node1.channels.append(channel)
        node2.channels.append(channel)
        if height > Channel.max_height:
            Channel.max_height = height
        return channel

    @staticmethod
    def destroy_channel(channel):
        channel.node1.channels.remove(channel)
        channel.node2.channels.remove(channel)

    def __contains__(self, item):
        if isinstance(item, Node):
            return item == self.node1 or item == self.node2
        return False

    def __repr__(self):
        return f'channel: {self.node1}->{self.node2}'

    # TODO we don't need the mongo-db stuff, right?
    def to_mongo(self) -> str:
        return self.node1.name + ',' + self.node2.name
