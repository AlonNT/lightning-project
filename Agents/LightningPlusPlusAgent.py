from typing import List, Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from Agents.AbstractAgent import AbstractAgent


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
    # n = len(graph.nodes)
    n = len(nodes)  # TODO: is it ok? i want to call graph.nodes only once in order to allow excluding nodes
    distance_matrix = np.empty(shape=(n, n), dtype=np.float32)

    for source_node, distances_to_targets in nx.shortest_path_length(graph):
        if source_node in nodes:  # TODO: is this too slow?
            i = nodes.index(source_node)
            for target_node, distance in distances_to_targets.items():
                j = nodes.index(target_node)
                distance_matrix[i, j] = distance

    return distance_matrix


def visualize_current_step(graph, nodes, positions,  agent_node, selected_node, selected_nodes, p, i, k):
    """
    Visualize a single step in the nodes selection algorithm.

    :param graph: The graph.
    :param nodes: A list of nodes (important for the order of the nodes).
    :param positions: The positions of the graph to plot.
    :param agent_node: The agent's node (will be plotted in yellow).
    :param selected_node: The current selected node (will be plotted in green).
    :param selected_nodes: The list of the selected nodes so far (will be plotted in magenta).
    :param p: The current probability vector (each node's probability will be plotted above it).
    :param i: The iteration number (will be added to the plot title).
    :param k: The total number of iterations (will be added to the plot title).
    """
    plt.figure()
    plt.title(f'Iteration #{i + 1} in selecting {k} best nodes')
    nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')
    for node, (x, y) in positions.items():
        plt.text(x - 0.02, y + 0.05, s='{:.2f}'.format(p[nodes.index(node)]))

    nx.draw_networkx_nodes(graph, positions, nodelist=[agent_node], node_color='yellow', alpha=1)
    nx.draw_networkx_nodes(graph, positions, nodelist=selected_nodes, node_color='magenta', alpha=1)
    nx.draw_networkx_nodes(graph, positions, nodelist=[selected_node], node_color='green', alpha=1)
    plt.show()


def find_best_k_nodes(graph, k, agent_public_key, visualize=False):
    """
    Find the best k nodes in the given graph,
    where 'best' means that they have high total capacities
    and they are distant from each other.

    :param graph: The graph.
    :param k: The number of nodes to select.
    :param agent_public_key: The agent's public key, needed in order to exclude it from the selection.
    :param visualize: If it's true, visualize each step in the algorithm.
    :return: A list containing the k selected nodes.
    """
    agent_node = graph.nodes[agent_public_key]
    nodes = list(graph.nodes)
    distance_matrix = get_distance_matrix(graph, nodes)

    positions = nx.spring_layout(graph)

    selected_nodes = list()

    for i in range(k):
        possible_nodes_mask = np.array([(node not in selected_nodes) for node in nodes])
        capacities_p = get_capacities_probability_vector(graph, nodes, possible_nodes_mask)
        distances_p = get_distances_probability_vector(nodes, possible_nodes_mask, distance_matrix)
        combined_p = capacities_p * distances_p
        combined_p[nodes.index(agent_node)] = 0  # Exclude the agent's node from the distribution.
        p = combined_p / combined_p.sum()

        selected_node = np.random.choice(nodes, p=p)
        selected_nodes.append(selected_node)

        if visualize:
            visualize_current_step(graph, nodes, positions, agent_node, selected_node, selected_nodes, p, i, k)

    return selected_nodes


class LightningPlusPlusAgent(AbstractAgent):
    def __init__(self, public_key, initial_funds, channel_cost, **kwargs):
        super(LightningPlusPlusAgent, self).__init__(public_key, initial_funds, channel_cost)
        self.alpha = kwargs['alpha']

    @property
    def name(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(alpha={self.alpha})'

    def get_channels(self, graph: nx.MultiGraph) -> List[Dict]:
        return list()

    # TODO keep this for he future use of RL.
    # def act(self, graph):
    #     if self.nodes_to_connect is None:
    #         self.nodes_to_connect = find_best_k_nodes(graph, self.max_edges, exclude_nodes=[self.pub_key])
    #     if self.added_edges < self.max_edges:
    #         other_node = self.nodes_to_connect[self.added_edges]
    #         self.added_edges += 1
    #         p = 0.5
    #         self.balance -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
    #         command_arguments = {'node1_pub': self.pub_key, 'node2_pub': other_node,
    #                              'node1_policy': LND_DEFAULT_POLICY,
    #                              'balance_1': p * self.default_channel_capacity,
    #                              'balance_2': (1 - p) * self.default_channel_capacity}
    #         return 'add_edge', list(command_arguments.values())
    #     return 'NOOP', {}
