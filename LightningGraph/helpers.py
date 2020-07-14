from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph

def create_sub_graph_by_highest_node_capcity(dump_path, k = 64):
    graph = read_data_to_xgraph(dump_path)
    process_lightning_graph(graph, remove_isolated=True, total_capacity=True)

    sorted_nodes = sorted(graph.nodes, key=lambda node: graph.nodes[node]['total_capacity'], reverse=True)
    best_nodes = sorted_nodes[:k]
    print("Creating sub graph with %d/%d nodes"%(k, len(sorted_nodes)))
    graph = graph.subgraph(best_nodes)
    process_lightning_graph(graph, remove_isolated=False, total_capacity=False, compute_betweeness=True, infer_imp=True)
    return graph
