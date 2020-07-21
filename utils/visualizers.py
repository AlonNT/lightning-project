import networkx as nx
from utils.common import human_format
from typing import List, Tuple
from matplotlib import pyplot as plt

def visualize_balances(graph):
    positions = nx.spring_layout(graph, seed=None)
    nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')
    edge_labels = {}
    for node1_pub, node2_pub, edge_data in graph.edges(data=True):
        node1_x, node1_y = positions[node1_pub]
        node2_x, node2_y = positions[node2_pub]
        if node1_x < node2_x:
            balance_left = human_format(edge_data['node1_balance'])
            balance_right = human_format(edge_data['node2_balance'])
        else:
            balance_left = human_format(edge_data['node2_balance'])
            balance_right = human_format(edge_data['node1_balance'])

        edge_labels[(node1_pub, node2_pub)] = f"{balance_left}<->{balance_right}"
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_color='red', font_size=8)
    plt.show()


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