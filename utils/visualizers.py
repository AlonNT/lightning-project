import os
from typing import List, Tuple, Dict
import seaborn as sns
import pandas as pd
import numpy as np
import imageio
import networkx as nx
from matplotlib import pyplot as plt
from utils.common import human_format, get_sender_policy_and_id, PLT_COLORS


def visualize_graph_state(graph, positions, transfer_routes=None, verify_node_serial_number=False,
                          additional_node_info=None, plot_title="graph state", out_path=None):
    # TODO:  make this function modular by making it work on an input figure and adding info on it
    """Creates an image of the current state of a graph wtih channel balances on edges
    The transfer routes are portrayed too.
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

    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_color='red', font_size=9)
    nx.draw_networkx_labels(graph, positions, labels={n: graph.nodes[n]['serial_number'] for n in graph.nodes},
                            font_color='y', font_size=6)

    # Highlight specified routes
    if transfer_routes is not None:
        for i, (full_route, last_node_index) in enumerate(transfer_routes):
            src = full_route[0][0]
            dst = full_route[-1][1]
            c = PLT_COLORS[i]
            nx.draw_networkx_edges(graph, positions, edgelist=full_route[:last_node_index],
                                   edge_color=c, width=15, edgecolors='k', alpha=0.5)
            nx.draw_networkx_edges(graph, positions, edgelist=full_route[last_node_index:],
                                   edge_color=c, width=5, edgecolors='k', alpha=0.5)

            # Mark src and dest positions
            src_x, src_y = positions[src]
            dest_x, dest_y = positions[dst]
            plt.text(src_x, src_y, s='source', bbox=dict(facecolor=c, alpha=0.5))
            plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor=c, alpha=0.5))

    if additional_node_info is not None:
        for info in additional_node_info:
            x, y = positions[info]
            plt.text(x - 0.3, y + 0.1, s=additional_node_info[info], bbox=dict(facecolor='k', alpha=0.5))
    plt.title(plot_title)
    plt.tight_layout()
    if out_path is not None:
        plt.savefig(out_path)
    else:
        plt.show()

    plt.clf()


def visualize_routes(graph, src, dest, routes: Dict[str, List[Tuple[str, str]]]):
    """Plots the graph while highlighting specified routes, src and dest nodes and the fees on the specified routes"""
    # set nodes positions on the graph on a 2d space for visualization
    # random_state = np.random.RandomState(SEED)
    positions = nx.spring_layout(graph, seed=None)

    nx.draw(graph, positions, with_labels=False, font_weight='bold', node_color='k')

    # Add fee visualization on routes edges
    for i, route_name in enumerate(routes):
        edge_labels = {}
        route = routes[route_name]
        # Add fees visualization
        for edge_key in route:
            edge_data = graph.edges[edge_key]
            sender_node_policy, sender_node_id = get_sender_policy_and_id(edge_key[1], edge_data)
            edge_labels[(edge_key[0], edge_key[
                1])] = f'b:{sender_node_policy["fee_base_msat"]}\nr:{sender_node_policy["fee_rate_milli_msat"]}'

        nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_color='red', font_size=8)

        # Highlight routes
        route_nodes = [r[0] for r in route] + [route[-1][1]]
        # nx.draw_networkx_nodes(graph, positions, nodelist=route_nodes,
        #                        node_color=colors[i], edgecolors='k', alpha=0.5)
        nx.draw_networkx_edges(graph, positions, edgelist=route,
                               edge_color=PLT_COLORS[i], width=10, edgecolors='k', label=route_name, alpha=0.5)

    # Mark src and dest positions
    src_x, src_y = positions[src]
    dest_x, dest_y = positions[dest]
    plt.text(src_x, src_y, s='source', bbox=dict(facecolor='green', alpha=0.5))
    plt.text(dest_x, dest_y, s='target', bbox=dict(facecolor='red', alpha=0.5))

    plt.legend()
    plt.show()


def create_simulation_gif(folder):
    file_names = sorted([os.path.join(folder, filename) for filename in os.listdir(folder)])
    images = [imageio.imread(fn) for fn in file_names]
    # with imageio.get_writer(os.path.join(os.path.dirname(folder), "simulation.gif"), mode='I') as  writer:
    #     for filename in os.listdir(folder):
    #         image = imageio.imread(os.path.join(folder, filename))
    #         writer.append_data(image)
    imageio.mimsave(os.path.join(os.path.dirname(folder), "simulation.gif"), images,
                    duration=0.5)  # modify the frame duration as needed


def plot_experiment_mean_and_std(values: np.array, label: str, color, use_seaborn=True):
    """Plot the mean and std of n experiment with m steps
        param:values: an n x m array describing the comulative reward of n experiments of a single agent
    """
    if use_seaborn:
        # TODO this is super Slow!
        print("Plotting with Seaborn")
        dfs = []
        # Create a dataframe with multiple experiment, sns.lineplot needs them to have a
        # common x values in order to compute mean and std
        for r in range(len(values)):
            df_row = pd.DataFrame(values[r])
            df_row['x'] = df_row.index
            dfs += [df_row]
        data = pd.concat(dfs)
        sns.lineplot(x='x', y=0, data=data, label=label, color=color)
    else: # PLT lame version
        mean = values.mean(0)
        std = values.std(0)*0.5 # * 0.5 to make it smaller
        plt.plot(range(len(mean)), mean, color=color, label=label)
        plt.errorbar(range(len(mean)), mean, std, color=color, alpha=0.3)
