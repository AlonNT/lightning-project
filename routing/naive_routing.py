import networkx as nx
from typing import List

def get_channel_with_minimal_fee_base(subgraph: nx.MultiGraph, source, target):
    """
    Get a sub-graph containing exactly two nodes - one is the source and the other is the destination.
    The function calculate the channel with the minimal base-fee and returns it.

    :param subgraph: The MultiGraph containing the nodes src and dest.
    :param source: The source node.
    :param target: The target node.
    :return: The channel with the minimal base-fee.
    """
    assert set(subgraph.nodes) == {source, target}, \
        "BAD USAGE - you should give a graph containing only the two given nodes"

    min_fee: float = float('inf')
    min_fee_channel_id = None

    for node1, node2, channel_data in subgraph.edges(data=True):
        if source == channel_data['node1_pub']:
            source_i, target_i = 1, 2
        elif source == channel_data['node2_pub']:
            source_i, target_i = 2, 1
        else:
            assert False, "WTF? Neither 'source' nor 'target' are in the channel."

        # When money is transferred from the source node to the target node, the fee is paid for the target node
        # (i.e. that target node keeps some of the money to himself, and passes the rest forwards).
        channel_fee: float = channel_data[f'node{target_i}_policy']['fee_base_msat']

        if channel_fee < min_fee:
            min_fee = channel_fee
            min_fee_channel_id = (channel_data[f'node{source_i}_pub'], channel_data[f'node{target_i}_pub'],
                                  channel_data['channel_id'])

    assert (min_fee_channel_id is not None) and (min_fee != float('inf')), "ERROR: no channel was chosen."

    return min_fee_channel_id


def nodes_list_to_edges(graph: nx.MultiGraph, nodes_list: List) -> List:
    """
    Get a graph and a list of nodes - the first node in the list is the source node, and the last is the target node.
    The function calculates for every two adjacent nodes the edge with the minimal base-fee
    (since there might be multiple edges between two nodes - it's a MultiGraph).

    :param graph: The MultiGraph to process.
    :param nodes_list: The list of nodes describing a path.
    :return: A list of edges in the graph, each one is the edge in the path.
    """
    edges_list = list()

    for i in range(len(nodes_list) - 1):
        node1 = nodes_list[i]
        node2 = nodes_list[i+1]
        subgraph = graph.subgraph(nodes=(node1, node2))
        min_fee_channel = get_channel_with_minimal_fee_base(subgraph, source=node1, target=node2)
        edges_list.append(min_fee_channel)

    return edges_list


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
