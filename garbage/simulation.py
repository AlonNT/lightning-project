import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple
import random
import numpy as np
from garbage import channel, node

dispatcher = {
    'complete_graph': nx.complete_graph,
    'cycle_graph': nx.cycle_graph,
    'ladder_graph': nx.ladder_graph,
    'star_graph': nx.star_graph,
    'wheel_graph': nx.wheel_graph
}


def create_graph(graph_type: str, n: int):
    """

    :param graph_type:
    :param n:
    :return:
    """

    # TODO daniel - get the graph type and return a graph with our objects
    if graph_type not in dispatcher:
        raise ValueError('graph_type {} is not in the dispatcher.'.format(graph_type))

    graph: nx.Graph = dispatcher[graph_type](n)

    pass


def create_random_nodes_objects(number_of_nodes: int) -> List[node.Node]:
    nodes_list: List[node.Node] = list()
    for i in range(number_of_nodes):
        nodes_list.append(node.Node(str(i)))
    return nodes_list


def create_random_channels(nodes_list: List[node.Node], number_of_channels: int) -> List[channel.Channel]:
    channels_list: List[channel.Channel] = list()
    for i in range(number_of_channels):
        nodes_indices: List[int] = random.sample(range(0, len(nodes_list) - 1), 2)
        balances_list: List[int] = random.sample(range(0, 5), 2)

        nodes: Tuple[int, int] = (nodes_list[nodes_indices[0]], nodes_list[nodes_indices[1]])
        balances: Tuple(int, int) = (balances_list[0], balances_list[1])

        channels_list.append(channel.Channel(nodes, balances))

    return channels_list


def create_graph_from_objects(nodes: List[node.Node], edges: List[channel.Channel], draw_graph: bool) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    # TODO check how to get to edges object from the graph (we can get the nodes attr via nodes_list)
    for edge in edges:
        graph.add_edge(edge.nodes[0], edge.nodes[1], object=edge)

    if draw_graph:
        plt.figure()
        nx.draw_networkx(graph, with_labels=True)
        plt.show()

    return graph


def transfer_money_between_two_nodes(amount: int, graph: nx.Graph):
    """
    Simulates money transformation between two nodes
    :param amount:
    :return:
    """
    # TODO needs the routing algorithm to check if it works

    # Get two different nodes
    v1: node.Node = np.random.choice(graph.nodes())
    v2: node.Node = np.random.choice(graph.nodes())
    while v1 == v2:
        v1 = np.random.choice(graph.nodes())
        v2 = np.random.choice(graph.nodes())

    if v1.send(v2.address, amount):
        print(f"Sent {amount} successfully")

    print(f"Failed Sending {amount}")


def sanity_main():
    """
    In this function we check that our assumptions about the routing in the network are correct.
    We will simulate a small network architecture, route transactions, and check the paths.
    The architecture will be as follow:
                src_node
              //        \\
 light edge //           \\ heavy edge
           //             \\
        node1            node2
          \\              //
    light  \\           //  light
            \\        //
              dst_node
    And we will check that when routing from src to dst, all the routes will go to node1.
    """
    src_node = node.Node("src")
    node1 = node.Node("node1")
    node2 = node.Node("node2")
    dst_node = node.Node("dst")
    channels = [
        channel.Channel(nodes=(src_node, node1), balances=(2, 3), base_fee=10),
        channel.Channel(nodes=(src_node, node2), balances=(2, 3), base_fee=1000),
        channel.Channel(nodes=(node1, dst_node), balances=(2, 3), base_fee=1000),
        channel.Channel(nodes=(node2, dst_node), balances=(2, 3), base_fee=1000)]

    # stubs, addrs = run_simulation([src_node, node1, node2, dst_node], channels)
    # path = stubs[src_node].QueryRoutes(ln.QueryRoutesRequest(pub_key=addrs[dst_node].pubkey, amt=1000))
    # path = [hop.pub_key for hop in path.routes[0].hops]
    # assert path == [addrs[node1].pubkey, addrs[dst_node].pubkey]
    # print("Success")


def main():
    pass

if __name__ == "__main__":
    nodes_list: List[node.Node] = create_random_nodes_objects(6)
    channels_list: List[channel.Channel] = create_random_channels(nodes_list, 3)
    graph = create_graph_from_objects(nodes_list, channels_list, False)
    transfer_money_between_two_nodes(1, graph)
    stop = "stop here"
    # sanity_main()