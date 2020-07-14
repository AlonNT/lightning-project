import networkx as nx
from typing import List
from routing.route_selection import get_route


class Manager:
    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph

    def transfer(self, amount: int, src, dst):
        path: List[nx.Graph.edges] = get_route(self.graph, src, dst)

    def get_state(self):
        return self.graph

    def step(self, action) -> nx.Graph:
        if action[0] == "add_edge":
            self.add_edge(*action[1])
        elif action[0] == "NOOP":
            pass
        else:
            raise ValueError(f"{action} not supported ")

        return self.graph

    def is_transfer_valid(self, amount: int):
        pass

    def create_agent_node(self):
        pub_key = len(self.graph.nodes) + 1
        self.graph.add_node(pub_key)
        return pub_key

    def add_edge(self, pub_key_node1, pub_key_node2, node1_balance, node2_balance):
        capacity = node1_balance + node2_balance
        self.graph.add_edge(pub_key_node1, pub_key_node2, capcity=capacity,
                            node1_balance=node1_balance, node2_balance=node2_balance)

    def get_node_balance(self, node1_pub_key):
        connected_edges = self.graph.edges(nbunch=node1_pub_key, data=True)
        return 1


#
# def initialize_graph(type: str) -> nx.Graph:
#     pass
