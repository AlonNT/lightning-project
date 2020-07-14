from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph
import networkx as nx

def create_sub_graph_by_highest_node_capacity(dump_path='./LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json', k=64):
    graph = read_data_to_xgraph(dump_path)
    process_lightning_graph(graph, remove_isolated=True, total_capacity=True)

    sorted_nodes = sorted(graph.nodes, key=lambda node: graph.nodes[node]['total_capacity'], reverse=True)
    best_nodes = sorted_nodes[:k]
    print("Creating sub graph with %d/%d nodes"%(k, len(sorted_nodes)))
    # graph = nx.Graph(graph.subgraph(best_nodes))
    process_lightning_graph(graph, remove_isolated=False, total_capacity=False, compute_betweeness=False, infer_imp=True)
    return graph
