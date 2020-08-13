import json
import random
import networkx as nx
from LightningGraph.lightning_implementation_inference import infer_node_implementation


def _compute_total_node_capacity(graph, node):
    """
    Sum the capacities in all edges touching a given node
    """
    neighbours = graph.adj[node]._atlas
    return sum([neighbours[adj_node_id][channel_id]['capacity']
                for adj_node_id in neighbours for channel_id in neighbours[adj_node_id]])


def _filter_nonvalid_data(json_data):
    """
    Remove channels that are disabled or that do not declare their policies.
    """
    # Filter to channels having both peers exposing their policies
    json_data['edges'] = list(filter(lambda x: x['node1_policy'] and x['node2_policy'], json_data['edges']))

    # Filter to non disabled channels
    json_data['edges'] = list(filter(lambda x: not (x['node1_policy']['disabled'] or x['node2_policy']['disabled']),
                                     json_data['edges']))

    return json_data


def cast_channel_data(channel):
    """
    Convert numeric parameter values (integers) that are held as strings to their natural form (int).
    :param channel: The channel to cast its values to integers.
    """
    channel['capacity'] = int(channel['capacity'])
    for i in [1, 2]:
        policy_key = f'node{i}_policy'
        if channel[policy_key]:
            for value_key in ['min_htlc', 'fee_base_msat', 'fee_rate_milli_msat']:
                channel[policy_key][value_key] = float(channel[policy_key][value_key])

            # The "fee_rate_milli_msat" entry describes the proportional fees. Instead of a float or
            # denominator numerator ints it is given as an integer that needs to be divided by 1000
            # therefore the word milli.
            channel[policy_key]['proportional_fee'] = float(channel[policy_key]['fee_rate_milli_msat']) / 1000


def read_data_to_xgraph(json_path):
    """Create an undirected multigraph using networkx and load the data to it"""
    # Read json file created by LND describegraph command on the mainnet.
    json_data = json.load(open(json_path, 'r', encoding="utf8"))
    json_data = _filter_nonvalid_data(json_data)
    graph = nx.MultiGraph()
    for i, node_data in enumerate(json_data['nodes']):
        pub_key = node_data.pop('pub_key', None)
        graph.add_node(pub_key, pub_key=pub_key, serial_number=i)
    for edge_data in json_data['edges']:
        cast_channel_data(edge_data)
        graph.add_edge(edge_data['node1_pub'], edge_data['node2_pub'], edge_data['channel_id'], **edge_data)
    
    return graph


def process_lightning_graph(graph,
                            remove_isolated=False,
                            total_capacity=False,
                            infer_implementation=False,
                            add_dummy_balances=True):
    """
    Analyze graph and add additional attributes.

    :param graph: The graph to process.
    :param remove_isolated: If True - remove isolated vertices from the graph.
                            This makes sense as they can not send/receive money,
                            and can not participate in other nodes transfers' routes.
    :param total_capacity: If True, add the total capacity for each node in the graph.
                           The total capacity is the sum of the capacities of all channels this node is involved in.
                           Currently used only to sort the nodes by importance for subgraphing the entire network
    :param infer_implementation: If True, infer the implementation of the nodes according to a simple heuristic
                                 involving the default values of their policies.
    :param add_dummy_balances: If True, assign dummy balances for each node in each channel,
                               by distributing the channel capacity randomly between the two nodes.
    """
    if remove_isolated:
        graph.remove_nodes_from(list(nx.isolates(graph)))

    # Sets node's total capacity (sum of the capacities on its adjacent edges)
    if total_capacity:
        for node in graph.nodes:
            graph.nodes[node]['total_capacity'] = _compute_total_node_capacity(graph, node)

    # Set's node routing implementation names
    if infer_implementation:
        for node in graph.nodes:
            graph.nodes[node]['routing_implementation'] = infer_node_implementation(node, graph.adj[node]._atlas)

    if add_dummy_balances:
        for edge in graph.edges:
            capacity = graph.edges[edge]['capacity']
            node1_balance_ratio = random.random()
            node2_balance_ratio = 1 - node1_balance_ratio
            graph.edges[edge]['node1_balance'] = node1_balance_ratio * capacity
            graph.edges[edge]['node2_balance'] = node2_balance_ratio * capacity
