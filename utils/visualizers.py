import os
from typing import List, Tuple, Dict
# import seaborn as sns
import pandas as pd
import numpy as np
import imageio
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm

from utils.common import human_format, get_sender_policy_and_id


def visualize_graph_state(graph, positions, transfer_routes=None, verify_node_serial_number=False,
                          plot_title="graph state", out_path=None):
    """
    Creates an image of the current state of a graph wtih channel balances on edges
    The transfer routes are portrayed too.
    param: verify_node_serial_number: print serial number alongside the balances too make sure they are on the right
            siide of the edges
    """
    plt.figure(3, figsize=(9, 9))
    nx.draw_networkx(graph, positions, with_labels=False, font_weight='bold', node_color='k', node_size=400)

    # Draw Channel balances
    edge_labels = {}
    for _, _, edge_data in graph.edges(data=True):  # order of nodes may differ so use edge_data['node{i}_pub']
        node1_x, node1_y = positions[edge_data['node1_pub']]
        node2_x, node2_y = positions[edge_data['node2_pub']]
        if node1_x < node2_x:
            debug_serial_left = graph.nodes[edge_data['node1_pub']]['serial_number']
            debug_serial_right = graph.nodes[edge_data['node2_pub']]['serial_number']
            balance_left = human_format(edge_data['node1_balance'])
            balance_right = human_format(edge_data['node2_balance'])
        else:
            debug_serial_left = graph.nodes[edge_data['node2_pub']]['serial_number']
            debug_serial_right = graph.nodes[edge_data['node1_pub']]['serial_number']
            balance_left = human_format(edge_data['node2_balance'])
            balance_right = human_format(edge_data['node1_balance'])

        if verify_node_serial_number:
            edge_labels[(edge_data['node1_pub'], edge_data[
                'node2_pub'])] = f"({debug_serial_left}){balance_left} : {balance_right}({debug_serial_right})"
        else:
            edge_labels[(edge_data['node1_pub'], edge_data['node2_pub'])] = f"{balance_left} : {balance_right}"

    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_color='red', font_size=7)
    nx.draw_networkx_labels(graph, positions, labels={n: graph.nodes[n]['serial_number'] for n in graph.nodes},
                            font_color='y', font_size=6)

    # Highlight specified routes
    if transfer_routes is not None:
        colors = cm.rainbow(np.linspace(0, 1, len(transfer_routes)))
        for i, (full_route, last_node_index) in enumerate(transfer_routes):
            c = colors[i]
            nx.draw_networkx_edges(graph, positions, edgelist=full_route[:last_node_index],
                                   edge_color=c, width=15, edgecolors='k', alpha=0.5)
            nx.draw_networkx_edges(graph, positions, edgelist=full_route[last_node_index:],
                                   edge_color=c, width=5, edgecolors='k', alpha=0.5)

            src = full_route[0][0]
            dst = full_route[-1][1]
            # Mark src and dest positions
            src_x, src_y = positions[src]
            dest_x, dest_y = positions[dst]
            plt.text(src_x, src_y, s='source', bbox=dict(facecolor=c, alpha=0.5))
            plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor=c, alpha=0.5))

    plt.title(plot_title)
    plt.tight_layout()
    if out_path is not None:
        plt.savefig(out_path)
    else:
        plt.show()
    plt.clf()


def create_simulation_gif(folder):
    file_names = sorted([os.path.join(folder, filename) for filename in os.listdir(folder)])
    images = [imageio.imread(fn) for fn in file_names]
    # with imageio.get_writer(os.path.join(os.path.dirname(folder), "simulation.gif"), mode='I') as  writer:
    #     for filename in os.listdir(folder):
    #         image = imageio.imread(os.path.join(folder, filename))
    #         writer.append_data(image)
    imageio.mimsave(os.path.join(os.path.dirname(folder), "simulation.gif"), images,
                    duration=0.5)  # modify the frame duration as needed


def plot_experiment_mean_and_std(values, ax, color_mapping=None):
    """
    Plot the mean and std of n experiment with m steps.
    :param values: dict maping an agent name to An n x m numpy array describing the cumulative
                    reward of n experiments of a single agent
    """
    m = next(iter(values.values())).shape[1]
    xs = range(m)
    if color_mapping is None:
        rainbow = cm.rainbow(np.linspace(0, 1, len(values)))
        color_mapping = dict(zip(values.keys(), rainbow))

    for agent_name in values:

        mean = values[agent_name].mean(0)
        ax.plot(xs, mean, color=color_mapping[agent_name], label=agent_name,  linewidth=4)

        # Plot error
        # option 1: plot all area between min and max plots; good when using few repeats
        ax.fill_between(xs, values[agent_name].min(0), values[agent_name].max(0), alpha=0.1,
                        color=color_mapping[agent_name])

        # option 2:
        # plot std error bats
        # error_plot_sparcity = 1000
        # std = values[agent_name].std(0) # * 0.5 to make it smaller
        # ax.errorbar(xs[::m//error_plot_sparcity], mean[::m//error_plot_sparcity],
        #              std[::m//error_plot_sparcity], color=color_mapping[agent_name], alpha=0.1)

        # # option 3
        # # plot all experiments
        # for row in values[agent_name]:
        #     ax.plot(xs, row, color=color_mapping[agent_name], linewidth=1)
