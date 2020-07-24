import argparse

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from LightningGraph.LN_parser import process_lightning_graph
from utils.graph_helpers import create_sub_graph_by_node_capacity


def get_distances_probability_vector(nodes, possible_nodes_mask, distance_matrix):
    """
    Get the distances probability vector for the nodes in the graph.
    Sampling a node according to this probability vector will (probably) result
    in a node that is far away from the already chosen nodes.

    :param nodes: A list of the nodes in the graph.
                  This is important because we want the order of the nodes to be the same,
                  and calling graph.nodes does not necessarily maintain the order. TODO or is it?
    :param possible_nodes_mask: A boolean NumPy array indicating whether the relevant node is possible for selection
                                or was it selected already.
    :param distance_matrix: A 2D NumPy array which is the distance between every two vertices in the graph.
                            Speeds up the run-time of this function.
    :return: A NumPy array that is a probability vector for the nodes in the graph.
    """
    # TODO consider taking a different distance function, such as the number of paths between two vertices
    #     lengths = np.array([len(list(nx.all_simple_paths(graph, source=u, target=v)))
    #                         for u in graph.nodes for v in graph.nodes if u != v])
    n = len(nodes)

    if np.all(possible_nodes_mask):
        return np.ones(shape=n, dtype=np.float32)

    distances_p = np.empty(shape=n, dtype=np.float32)
    for i, distances in enumerate(distance_matrix):  # TODO Do it vectorized
        distances_p[i] = np.min(distances[~possible_nodes_mask])

    return distances_p


def get_capacities_probability_vector(graph, nodes, possible_nodes_mask, alpha=2):
    """
    Get the capacities probability vector for the nodes in the graph.
    Sampling a node according to this probability vector will (probably) result in a node with high capacity.

    :param graph: The graph.
    :param nodes: A list of the nodes in the graph.
                  This is important because we want the order of the nodes to be the same,
                  and calling graph.nodes does not necessarily maintain the order. TODO or is it?
    :param possible_nodes_mask: A boolean NumPy array indicating whether the relevant node is possible for selection
                                or was it selected already.
    :param alpha: The power to raise the capacities before dividing by the sum.
                  Higher values enlarge the differences between the resulting probabilities
                  for node with different capacities.
    :return: A NumPy array that is a probability vector for the nodes in the graph.
    """
    if possible_nodes_mask is None:
        possible_nodes_mask = np.ones(shape=len(nodes), dtype=np.bool)

    capacities_per_node = nx.get_node_attributes(graph, 'total_capacity')
    capacities = np.array([capacities_per_node[node] for node in nodes])
    capacities[~possible_nodes_mask] = 0
    capacities_to_the_power_of_alpha = capacities ** alpha
    p = capacities_to_the_power_of_alpha / capacities_to_the_power_of_alpha.sum()

    return p


def get_distance_matrix(graph, nodes):
    """
    Get a distance matrix for the nodes in the graph.

    :param graph: The graph.
    :param nodes: A list of the nodes in the graph.
                  This is important because we want the order of the nodes to be the same,
                  and calling graph.nodes does not necessarily maintain the order. TODO or is it?
    :return: A 2D NumPy array which is the distance between every two vertices in the graph.
    """
    n = len(graph.nodes)
    distance_matrix = np.empty(shape=(n, n), dtype=np.float32)

    for source_node, distances_to_targets in nx.shortest_path_length(graph):
        i = nodes.index(source_node)
        for target_node, distance in distances_to_targets.items():
            j = nodes.index(target_node)
            distance_matrix[i, j] = distance

    return distance_matrix


def find_best_k_nodes(graph, k, visualize=False):
    """
    Find the best k nodes in the given graph, where 'best' means that they have high total capacities
    and they are distant from each other.

    :param graph: The graph.
    :param k: The number of nodes to select.
    :param visualize: If it's true, visualize each step in the algorithm.
    :return: A list containing the k selected nodes.
    """
    nodes = list(graph.nodes)
    distance_matrix = get_distance_matrix(graph, nodes)

    positions = nx.spring_layout(graph, seed=None)

    selected_nodes = list()

    for i in range(k):
        possible_nodes_mask = np.array([(node not in selected_nodes) for node in nodes])
        capacities_p = get_capacities_probability_vector(graph, nodes, possible_nodes_mask)
        distances_p = get_distances_probability_vector(nodes, possible_nodes_mask, distance_matrix)
        combined_p = capacities_p * distances_p
        p = combined_p / combined_p.sum()

        selected_node = np.random.choice(nodes, p=p)
        selected_nodes.append(selected_node)

        if visualize:
            plt.figure()
            plt.title(f'Iteration #{i+1} in selecting {k} best nodes')
            nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')
            for node, (x, y) in positions.items():
                plt.text(x-0.02, y+0.05, s='{:.2f}'.format(p[nodes.index(node)]))

            nx.draw_networkx_nodes(graph, positions, nodelist=selected_nodes, node_color='magenta', alpha=1)
            nx.draw_networkx_nodes(graph, positions, nodelist=[selected_node], node_color='green', alpha=1)
            plt.show()

    return selected_nodes


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--num_nodes', type=int, default=12,
                        help='Parameter for the graph generator '
                             '(usually it\'s the number of vertices or something related to that).')
    parser.add_argument('-hco', '--highest_capacity_offset', type=int, default=48,
                        help='Parameter for the graph generator - will take the largest \'num_nodes\' nodes after the '
                             'first \'highest_capacity_offset\' in the descending order.')

    return parser.parse_args()


def main():
    args = parse_args()

    graph = create_sub_graph_by_node_capacity(k=args.num_nodes,
                                              highest_capacity_offset=args.highest_capacity_offset)
    process_lightning_graph(graph,
                            remove_isolated=False,
                            total_capacity=True,
                            infer_implementation=False,
                            compute_betweenness=False,
                            add_dummy_balances=True)

    find_best_k_nodes(graph, 3, visualize=True)


if __name__ == '__main__':
    main()
