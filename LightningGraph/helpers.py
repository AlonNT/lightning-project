from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph

# LIGHTNING_GRAPH_DUMP_PATH = './old_dumps/LN_2020.05.13-08.00.01.json' # TODO: this just does not work


def create_sub_graph_by_node_capacity(dump_path, k=64, highest_capacity_offset=0):
    """
    Creates a sub graph with at most k nodes. select nodes by their total capacities
    :param highest_capacity_offset: if 0 takes the highest 'k' nodes if its m, takes the k first after the first m nodes
                                    this is used to get a less connected graph. cant take lowest nodes as removing high
                                    nodes ussualy makes the graph highly unconnected.
    return: a connected graph with at most k nodes
    """
    graph = read_data_to_xgraph(dump_path)
    process_lightning_graph(graph, remove_isolated=True, total_capacity=True, infer_implementation=True)

    sorted_nodes = sorted(graph.nodes, key=lambda node: graph.nodes[node]['total_capacity'], reverse=True)

    # cant take last nodes as removing highest capacity nodes makes most of them isolated
    best_nodes = sorted_nodes[highest_capacity_offset: k + highest_capacity_offset]
    print("Creating sub graph with %d/%d nodes" % (k, len(sorted_nodes)))
    graph = graph.subgraph(best_nodes).copy()  # without copy a view is returned and the graph can not be changed.

    process_lightning_graph(graph, remove_isolated=True) # This may return a graph with less than k nodes

    return graph
