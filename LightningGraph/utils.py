from LightningGraph.LN_parser import read_data_to_xgraph, process_lightning_graph
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import networkx as nx

LIGHTNING_GRAPH_DUMP_PATH = '../LightningGraph/old_dumps/LN_2020.05.13-08.00.01.json'


def get_sender_policy_and_id(receiver_node_id, edge_data: Dict) -> Tuple:
    """
    :param receiver_node_id: The receiver node id (i.e. public-key).
    :param edge_data: A dictionary containing the edge's attributes.
    :return: A tuple containing two elements:
                 (1) The policy of the sender (A dictionary containing the fee policy)
                 (2) The id (i.e. public-key) of the sender.
    """
    if receiver_node_id == edge_data['node1_pub']:
        sender_node_i = 2
    elif receiver_node_id == edge_data['node2_pub']:
        sender_node_i = 1
    else:
        raise ValueError(f'The given receiver_node_id {receiver_node_id} is not in the given edge_data {edge_data}.')

    sender_node_policy = edge_data[f'node{sender_node_i}_policy']
    sender_node_id = edge_data[f'node{sender_node_i}_pub']

    return sender_node_policy, sender_node_id


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

def calculate_route_fees(graph, route, amount):
    total_amount = amount
    fees = []
    for edge_key in route[::-1]:
        sender_policy, _ = get_sender_policy_and_id(edge_key[1], graph.edges[edge_key])
        fee = sender_policy['fee_base_msat'] + (total_amount * sender_policy['fee_rate_milli_msat'])
        fees += [fee]
        total_amount += fee

    return fees[::-1]

def visualize_routes(graph, src, dest, routes: List[Tuple[str, str]]):
    # set nodes positions on the graph on a 2d space for visualization
    # random_state = np.random.RandomState(SEED)
    positions = nx.spring_layout(graph, seed=None)

    nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')

    # colors = plt.cm.rainbow(np.linspace(0, 1, len(routes)))
    colors =['r','g','b','p','y']
    ## Add fee visualization on routes edges
    for i, route in enumerate(routes):
        edge_labels = {}
        for edge_key in route[1:]:
            edge_data = graph.edges[edge_key]
            sender_node_policy, sender_node_id = get_sender_policy_and_id(edge_key[1], edge_data)
            edge_labels[(edge_key[0], edge_key[1])] = f'b:{sender_node_policy["fee_base_msat"]}\nr:{sender_node_policy["fee_rate_milli_msat"]}'

        nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_color='red', font_size=8)

        ## Highlight routes
        route_nodes = [r[0] for r in route] + [route[-1][1]]

        nx.draw_networkx_nodes(graph, positions, nodelist=route_nodes,
                               node_color=colors[i], edgecolors='k', alpha=0.5)
        nx.draw_networkx_edges(graph, positions, edgelist=route,
                               edge_color=colors[i], width=10, edgecolors='k', label='naive', alpha=0.5)


    ## Mark src and dest positions
    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]
    plt.text(src_x, src_y, s='source', bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor='red', alpha=0.5))

    plt.legend()
    plt.show()