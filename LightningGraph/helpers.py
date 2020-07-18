from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph

LIGHTNING_GRAPH_DUMP_PATH = 'LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json'


def create_sub_graph_by_node_capacity(dump_path=LIGHTNING_GRAPH_DUMP_PATH, k=64, highest_capacity_offset=0):
    """
    Creates a sub graph with at most k nodes, selecting nodes by their total capacities.

    :param dump_path: The path to the JSON describing the lightning graph dump.
    :param k: The maximal number of nodes in the resulting graph.
    :param highest_capacity_offset: If it's 0, takes the k nodes with the highest capacity.
                                    If its m > 0, takes the k first nodes after the first m nodes.
                                    This is used to get a less connected graph.
                                    We can't take lowest nodes as removing high
                                    nodes usually makes the graph highly unconnected.
    :returns: a connected graph with at most k nodes
    """
    graph = read_data_to_xgraph(dump_path)
    process_lightning_graph(graph, remove_isolated=True, total_capacity=True, infer_implementation=True)

    sorted_nodes = sorted(graph.nodes, key=lambda node: graph.nodes[node]['total_capacity'], reverse=True)

    # Can't take last nodes as removing highest capacity nodes makes most of them isolated
    best_nodes = sorted_nodes[highest_capacity_offset: k + highest_capacity_offset]
    print("Creating sub graph with %d/%d nodes" % (k, len(sorted_nodes)))
    graph = graph.subgraph(best_nodes).copy()  # without copy a view is returned and the graph can not be changed.

    process_lightning_graph(graph, remove_isolated=True)  # This may return a graph with less than k nodes

    return graph
