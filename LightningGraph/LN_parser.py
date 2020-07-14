import json
from LightningGraph.lightning_implementation_inference import infer_node_implementation
import networkx as nx
from time import time

def _compute_total_node_capacity(neighbours):
    return sum([neighbours[adj_node_id][channel_id]['capacity'] for adj_node_id in neighbours for channel_id in neighbours[adj_node_id]])


def set_edges_betweenness(G):
    edge_betweenness = dict.fromkeys(G.edges, 0)
    edge_betweenness_by_pair_of_nodes = nx.edge_betweenness_centrality(G)
    for key in edge_betweenness:
        edge_betweenness[key] = edge_betweenness_by_pair_of_nodes[key[:2]]

    nx.set_edge_attributes(G, edge_betweenness, 'betweenness')


def _filter_nonvalid_data(json_data):
    """Remove channels that are disabled or that do not declare their policies."""
    # Filter to channels having both peers exposing their policies
    json_data['edges'] = list(filter(lambda x: x['node1_policy'] and x['node2_policy'], json_data['edges']))
    # Filter to non disabled channels
    json_data['edges'] = list(filter(lambda x: not (x['node1_policy']['disabled'] or x['node2_policy']['disabled']),
                                     json_data['edges']))
    # Require nodes to have valid pubkey
    json_data['nodes'] = list(filter(lambda x: not (x['pub_key']), json_data['nodes'])) # TODO this necesessary?

    return json_data

def cast_channel_data(channel):
    # Convert numeric parameter values (integers) that are held as strings to their natural form (int).
    channel['capacity'] = int(channel['capacity'])
    if channel['node1_policy']:
        channel['node1_policy']['min_htlc'] = int(channel['node1_policy']['min_htlc'])
        channel['node1_policy']['fee_base_msat'] = int(channel['node1_policy']['fee_base_msat'])
        channel['node1_policy']['fee_rate_milli_msat'] = int(channel['node1_policy']['fee_rate_milli_msat'])
    if channel['node2_policy']:
        channel['node2_policy']['min_htlc'] = int(channel['node2_policy']['min_htlc'])
        channel['node2_policy']['fee_base_msat'] = int(channel['node2_policy']['fee_base_msat'])
        channel['node2_policy']['fee_rate_milli_msat'] = int(channel['node2_policy']['fee_rate_milli_msat'])


def read_data_to_xgraph(json_path):
    """Create an undirected multigraph using networkx and load the data to it"""
    # Read json file created by LND describegraph command on the mainnet.
    json_data = json.load(open(json_path, 'r', encoding="utf8"))
    json_data = _filter_nonvalid_data(json_data)
    graph = nx.MultiGraph()
    graph.graph = {'network_capacity':0}
    for i, node_data in enumerate(json_data['nodes']):
        pub_key = node_data.pop('pub_key', None)
        graph.add_node(pub_key, node_data)
    for edge_data in json_data['edges']:
        # TODO: Can there be list pub_keys here?
        cast_channel_data(edge_data)
        graph.graph['network_capacity'] += edge_data['capacity']
        graph.add_edge(edge_data['node1_pub'], edge_data['node2_pub'], edge_data['channel_id'], **edge_data)
    
    return graph


def process_lightning_graph(graph, remove_isolated=True, total_capacity=True, infer_imp=False, compute_betweeness=False):
    """Analalyse graph and add additional attributes"""

    # Remove_isolated nodes
    if remove_isolated:
        graph.remove_nodes_from(list(nx.isolates(graph)))

    # Sets node's total capacity (sum of the capacities on its adjacent edges)
    if total_capacity:
        for node in graph.nodes:
            graph.nodes[node]['total_capacity'] = _compute_total_node_capacity(graph.adj[node]._atlas)

    # Set's node routing implementation names
    if infer_imp:
        for node in graph.nodes:
            if infer_imp:
                graph.nodes[node]['routing_implemenation'] = infer_node_implementation(node, graph.adj[node]._atlas)

    if compute_betweeness:
        timing_start = time()
        set_edges_betweenness(graph)
        print("Computing edges betweenes took %.5f sec"%(time()-timing_start))


