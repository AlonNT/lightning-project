import networkx as nx
from routing.utils import nodes_list_to_edges


def get_route(graph: nx.MultiGraph, source, target, amount):
    """
    A naive approach for getting the route between the source node and the destination node.
    It first gets the path of minimal length, and then for each one of the possibilities for channels between the
    two nodes, get the channel with the minimal base-fee.

    :param graph: The Graph.
    :param source: The source node.
    :param target: The target node.
    :return: The route chosen from the source to the target.
    """
    try:
        nodes_list = nx.shortest_path(graph, source, target)
    except nx.exception.NetworkXNoPath:
        print("Warning: | get_route | no path found between nodes")
        return None

    edges_list = nodes_list_to_edges(graph, nodes_list)

    return edges_list
