import random
from typing import List, Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from Agents.AbstractAgent import AbstractAgent
from utils.common import calculate_agent_policy


def get_distances_probability_vector(possible_nodes_mask: np.ndarray,
                                     distance_matrix: np.ndarray,
                                     alpha: float = 3) -> np.ndarray:
    """
    Get the distances probability vector for the nodes in the graph.
    Sampling a node according to this probability vector will (probably) result
    in a node that is far away from the already chosen nodes.

    :param possible_nodes_mask: A boolean NumPy array indicating whether the relevant node is
                                possible for selection or was it selected already.
    :param distance_matrix: A 2D NumPy array which is the distance between every two vertices
                            in the graph. Speeds up the run-time of this function.
    :param alpha: The power to raise the weights vector before dividing by the sum.
                  Higher values enlarge the differences between the resulting probabilities.
    :return: A NumPy array that is the probability vector for the nodes in the graph.
    """
    n = len(possible_nodes_mask)

    # This is a mask indicating the previously selected nodes.
    selected_nodes_mask = ~possible_nodes_mask

    # If all node are possible for the selection (meaning there are no nodes that
    # were already selected), the distances are undefined.
    # Return the all ones weight vector, so all nodes have the same weight.
    if np.all(possible_nodes_mask):
        weights_vector = np.ones(shape=n, dtype=np.float32)

    # Now we know that some nodes were selected, and the distances are well defined.
    # The weight of each node will be the minimal distance to a previously selected node.
    else:
        weights_vector = np.empty(shape=n, dtype=np.float32)
        for i, distances in enumerate(distance_matrix):
            weights_vector[i] = np.min(distances[selected_nodes_mask])

    weights_to_the_power_of_alpha = weights_vector ** alpha
    probability_vector = weights_to_the_power_of_alpha / weights_to_the_power_of_alpha.sum()

    return probability_vector


def get_capacities_probability_vector(graph: nx.MultiGraph,
                                      nodes: list,
                                      possible_nodes_mask: np.ndarray,
                                      alpha: float = 3) -> np.ndarray:
    """
    Get the capacities probability vector for the nodes in the graph.
    Sampling a node according to this probability vector will (probably)
    result in a node with high capacity.

    :param graph: The graph.
    :param nodes: A list of the nodes in the graph.
                  This is important because we want the order of the nodes to be the same,
                  and calling graph.nodes does not necessarily maintain the order.
    :param possible_nodes_mask: A boolean NumPy array indicating whether the relevant node is possible for selection
                                or was it selected already.
    :param alpha: The power to raise the capacities before dividing by the sum.
                  Higher values enlarge the differences between the resulting probabilities
                  for node with different capacities.
    :return: A NumPy array that is a probability vector for the nodes in the graph.
    """
    capacities_per_node = nx.get_node_attributes(graph, 'total_capacity')
    capacities = np.array([capacities_per_node[node] for node in nodes])
    capacities[~possible_nodes_mask] = 0
    q = capacities / capacities.sum()
    q_to_the_power_of_alpha = q ** alpha
    p = q_to_the_power_of_alpha / q_to_the_power_of_alpha.sum()

    return p


def get_distance_matrix(graph, nodes):
    """
    Get a distance matrix for the nodes in the graph.

    :param graph: The graph.
    :param nodes: A list of the nodes in the graph.
                  This is important because we want the order of the nodes to be the same,
                  and calling graph.nodes does not necessarily maintain the order.
    :return: A 2D NumPy array which is the distance between every two vertices in the graph.
    """
    n = len(nodes)
    distance_matrix = np.empty(shape=(n, n), dtype=np.float32)

    for source_node, distances_to_targets in nx.shortest_path_length(graph):
        i = nodes.index(source_node)
        for target_node, distance in distances_to_targets.items():
            j = nodes.index(target_node)
            distance_matrix[i, j] = distance

    return distance_matrix


def visualize_current_step(graph, nodes, positions, agent_node, selected_node, selected_nodes, p, i, k):
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
        if node == agent_node:  # There is no probability to plot for the agent node.
            continue
        plt.text(x - 0.02, y + 0.05, s='{:.2f}'.format(p[nodes.index(node)]))

    nx.draw_networkx_nodes(graph, positions, nodelist=[agent_node], node_color='yellow')
    nx.draw_networkx_nodes(graph, positions, nodelist=selected_nodes, node_color='magenta')
    nx.draw_networkx_nodes(graph, positions, nodelist=[selected_node], node_color='green')
    plt.show()


def find_best_k_nodes(graph, k, agent_public_key, alpha=3, visualize=False):
    """
    Find the best k nodes in the given graph,
    where 'best' means that they have high total capacities
    and they are distant from each other.

    :param graph: The graph.
    :param k: The number of nodes to select.
    :param agent_public_key: The agent's public key, needed in order to exclude it from the selection.
    :param alpha: The power to raise to probability vector.
                  The higher it is, the differences between high values and small values gets larger.
    :param visualize: If it's true, visualize each step in the algorithm.
    :return: A list containing the k selected nodes.
    """
    nodes = [node for node in graph.nodes if node != agent_public_key]
    sub_graph = graph.subgraph(nodes).copy()
    distance_matrix = get_distance_matrix(sub_graph, nodes)

    positions = nx.spring_layout(graph)

    selected_nodes = list()

    for i in range(k):
        possible_nodes_mask = np.array([(node not in selected_nodes) for node in nodes])
        capacities_p = get_capacities_probability_vector(sub_graph, nodes, possible_nodes_mask, alpha)
        distances_p = get_distances_probability_vector(possible_nodes_mask, distance_matrix)
        combined_p = capacities_p * distances_p
        p = combined_p / combined_p.sum()

        selected_node = np.random.choice(nodes, p=p)
        selected_nodes.append(selected_node)

        if visualize:
            visualize_current_step(graph, nodes, positions, agent_public_key, selected_node, selected_nodes, p, i, k)

    return selected_nodes


class LightningPlusPlusAgent(AbstractAgent):

    def __init__(self, public_key, initial_funds, channel_cost,
                 alpha=3, n_channels_per_node=4, money_in_each_channel=10**4):
        super(LightningPlusPlusAgent, self).__init__(public_key, initial_funds, channel_cost)

        self.alpha = alpha
        self.n_channels_per_node = n_channels_per_node
        self.money_in_each_channel = money_in_each_channel

    @property
    def name(self) -> str:
        """
        :return: The name of the agent.
        """
        class_name = self.__class__.__name__
        return f'{class_name}(a={self.alpha}, ' \
               f'n={self.n_channels_per_node}, ' \
               f'm={self.money_in_each_channel})'

    def get_channels(self, graph: nx.MultiGraph) -> List[Dict]:
        """
        This function gets the graph as and return the channels the agent wants to create.

        :param graph: The graph where the agent operates in.
        :return: A list containing the channels the agent wishes to create.
                 Each channel is a dictionary containing the relevant attributes.
        """
        channels = list()

        funds = self.initial_funds

        channel_creation_cost = self.channel_cost
        money_in_channel_cost = self.money_in_each_channel
        total_channel_cost = channel_creation_cost + money_in_channel_cost
        number_of_nodes_to_surround = funds // (self.n_channels_per_node * total_channel_cost)
        assert number_of_nodes_to_surround > 0, "Consider subtracting self.n_channels_per_node or the channel cost "
        nodes_to_surround = find_best_k_nodes(graph, k=number_of_nodes_to_surround,
                                              agent_public_key=self.pub_key, alpha=self.alpha, visualize=False)

        for node in nodes_to_surround:
            min_time_lock_delta, min_base_fee, min_proportional_fee = calculate_agent_policy(graph, node)
            neighbors = list(graph.neighbors(node))
            if len(neighbors) <= self.n_channels_per_node:
                nodes_to_connect_with = neighbors
            else:
                nodes_to_connect_with = random.sample(neighbors, k=self.n_channels_per_node)

            for node_to_connect in nodes_to_connect_with:
                p = 0.5
                funds -= total_channel_cost + p * money_in_channel_cost

                channel_details = {'node1_pub': self.pub_key,
                                   'node2_pub': node_to_connect,
                                   'node1_policy': {"time_lock_delta": min_time_lock_delta,
                                                    "fee_base_msat": min_base_fee,
                                                    "proportional_fee": min_proportional_fee},
                                   # node2_policy will be determined by the simulator
                                   'node1_balance': p * money_in_channel_cost,
                                   'node2_balance': (1 - p) * money_in_channel_cost}

                channels.append(channel_details)

        return channels

