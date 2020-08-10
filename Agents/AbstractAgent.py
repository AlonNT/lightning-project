import networkx as nx
from typing import List, Dict

class AbstractAgent(object):
    def __init__(self, public_key: str, initial_funds: int, channel_cost: int):
        self.pub_key: str = public_key
        self.initial_funds: int = initial_funds
        self.channel_cost = channel_cost

    @property
    def name(self) -> str:
        raise NotImplementedError("The agent must declare its name.")

    def get_channels(self, graph: nx.MultiGraph) -> List[Dict]:
        """
        This function gets the graph as and return the channels the agent wants to create.

        :param graph: The graph describing the agent.
        :return: A list containing the channels the agent wishes to create.
                 Each channel is a dictionary containing the relevant attributes.
        """
        raise NotImplementedError("The agent must implement this function, "
                                  "indicating which channels it wishes to create")
