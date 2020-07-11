import json
from lightning_implementation_inference import infer_node_implementation
import networkx as nx
from time import time


def _compute_total_node_capacity(neighbours):
    return sum([neighbours[adj_node_id][channel_id]['capacity'] for adj_node_id in neighbours for channel_id in neighbours[adj_node_id]])


def set_additional_node_attributes(G, total_capacity=True, infer_imp=False):
    """
    Sets node's total capacity (sum of the capacities on its adjacent edges)
    Set's node routing implementation names
    """
    for node in G.nodes:
        neighbours = G.adj[node]._atlas
        if total_capacity:
            G.nodes[node]['total_capacity'] = _compute_total_node_capacity(neighbours)
        if infer_imp:
            G.nodes[node]['routing_implemenation'] = infer_node_implementation(node, neighbours)


def set_edges_betweenness(G):
    edge_betweenness = dict.fromkeys(G.edges, 0)
    edge_betweenness_by_pair_of_nodes = nx.edge_betweenness_centrality(G)
    for key in edge_betweenness:
        edge_betweenness[key] = edge_betweenness_by_pair_of_nodes[key[:2]]

    nx.set_edge_attributes(G, edge_betweenness, 'betweenness')


def filter_nonvalid_data(json_data):
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


def construct_xgraph(data):
    """Create an undirected multigraph using networkx and load the data to it"""
    graph = nx.MultiGraph()
    graph.graph = {'network_capacity':0}
    for node_data in data['nodes']:
        # nodedata = dict((make_str(k), v) for k, v in d.items() if k != name)
        # nodedata = deepcopy(node_data) # TODO is copy relevant
        pub_key = node_data.pop('pub_key', None) # TODO copy needed?
    for edge_data in data['edges']:
        # TODO: Can there be list pub_keys here?
        cast_channel_data(edge_data)
        graph.graph['network_capacity'] += edge_data['capacity']
        graph.add_edge(edge_data['node1_pub'], edge_data['node2_pub'], edge_data['channel_id'], **edge_data)
    
    return graph


def get_lightning_graph(json_path, total_capacity=True, infer_imp=False, compute_betweeness=False):
    """Parse LN data and analysis on it inro a networkx graph"""
    ## 1.  Preprocess data
    # Read json file created by LND describegraph command on the mainnet.
    json_data = json.load(open(json_path, 'r', encoding="utf8"))
    json_data = filter_nonvalid_data(json_data)

    ## 2.  Load data into a networkx graph
    graph = construct_xgraph(json_data)

    ## 3. Process the raw data:

    # Remove isolated nodes
    graph.remove_nodes_from(list(nx.isolates(graph)))

    # Set routing type and node total capacity
    set_additional_node_attributes(graph, total_capacity=total_capacity, infer_imp=infer_imp) # Todo: consider removing unknown impl nodes

    if compute_betweeness:
        timing_start = time()
        set_edges_betweenness(graph)
        print("Computing edges betweenes took %.5f sec"%(time()-timing_start))

    print("Graph created: %d nodes, %d edges"%(len(graph.nodes), len(graph.edges)))
    return graph

