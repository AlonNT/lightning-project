from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph

LIGHTNING_GRAPH_DUMP_PATH = 'LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json'


def create_sub_graph_by_highest_node_capacity(dump_path=LIGHTNING_GRAPH_DUMP_PATH, k=64):
    graph = read_data_to_xgraph(dump_path)
    process_lightning_graph(graph, remove_isolated=True, total_capacity=True)

    sorted_nodes = sorted(graph.nodes, key=lambda node: graph.nodes[node]['total_capacity'], reverse=True)
    best_nodes = sorted_nodes[:k]
    print("Creating sub graph with %d/%d nodes" % (k, len(sorted_nodes)))
    graph = graph.subgraph(best_nodes).copy()  # without copy a view is returned and the graph can not be changed.
    process_lightning_graph(graph,
                            remove_isolated=False, total_capacity=False,
                            compute_betweenness=False, infer_implementation=True)
    return graph
