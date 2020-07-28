import networkx as nx

from typing import List, Dict, Union
from Agents.consts import DEFAULT_INITIAL_FUNDS


class AbstractAgent(object):
    def __init__(self, public_key: str, initial_funds: int = DEFAULT_INITIAL_FUNDS):
        self.pub_key: str = public_key
        self.initial_funds: int = initial_funds
        self.nodes_to_connect = None # Relevant for RL style simulations
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

    def act(self, graph):
        """This is relevnat to RL style simulations: Returns the selected edges one by one"""
        if self.nodes_to_connect is None:
            self.nodes_to_connect = self.get_channels(graph)
            self.added_edges = 0
        if self.added_edges < len(self.nodes_to_connect):
            command_arguments = self.nodes_to_connect[self.added_edges]
            self.added_edges += 1
            return 'add_edge', command_arguments
        return 'NOOP', {}
