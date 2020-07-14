import networkx as nx
from typing import List
from routing.route_selection import get_route

class Manager:

    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph
        self.counter = 0


    def transfer(self, amount: int, src, dst):
        path: List[nx.Graph.edges] = get_route(self.graph, src, dst)


    def get_state(self):
        return self.graph

    def step(self, action) -> nx.Graph:
        if action[0] == "add_edge":
            return self.add_edge(*action[1])
        else:
            raise ValueError(f"{action} not supported ")


    def route(self, routing_type: str) -> List[nx.Graph.edges]:
        pass

    def is_transfer_valid(self, amount: int):
        pass

    def create_agent_node(self):
        self.graph.add_node(len(self.graph.nodes) + 1)

    def add_edge(self, pub_key_node1, pub_key_node2, node1_balance, node2_balance) -> nx.Graph:
        capacity = node1_balance + node2_balance
        self.graph.add_edge(pub_key_node1, pub_key_node2, capcity=capacity,
                      node1_balance=node1_balance, node2_balance=node2_balance)
        return self.graph

    def get_node_balance(self, node1):
        connected_edges = self.graph.edges([node1])




def initialize_graph(type: str) -> nx.Graph:
    pass

