import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import cm
NUM_EDGES = [2, 4, 8, 16, 32]

AGENT_TYPES = ['Greedy-max-capacity', 'Greedy-max-routeness', 'Greedy-max-degree', 'LPP-max-capacity',
               'LPP-max-routeness', 'LPP-max-degree', 'Random']
COLORS=['darkgreen', 'seagreen', 'lime', 'midnightblue', 'royalblue', 'cornflowerblue', 'r']
D_COLORS=cm.rainbow(np.linspace(0, 1, len(NUM_EDGES)))

def get_agent_type(name):
    for t in AGENT_TYPES:
        if t in name:
            return t
    return None


def get_d_value(name):
    for d in NUM_EDGES:
        if f"d={d}" in name:
            return d
    return None


def capacity_vs_scarcity(results, out_folder):
    """
    Plot the effect of the d parameter per agent
    """
    fig = plt.figure(figsize=(12,8))
    for i, agent_type in enumerate(AGENT_TYPES):
        print("capacity_vs_scarcity: ", agent_type)
        ax = plt.subplot(3, 3, i+1)
        for agent_name in results:
            if agent_type in agent_name:
                color = D_COLORS[NUM_EDGES.index(get_d_value(agent_name))]
                xs = range(results[agent_name].shape[1])
                ax.plot(xs, results[agent_name].mean(0), color=color, linewidth=3)
                ax.fill_between(xs, results[agent_name].min(0), results[agent_name].max(0),
                                alpha=0.1, color=color)
                ax.title.set_text(agent_type)
                ax.set_xticks([])

    # Set empty plots just for getting a common legend for all subplots
    for name, color in zip(NUM_EDGES, D_COLORS):
       ax.plot([],[], color=color, label=f"d={name}")
    handles, labels = ax.get_legend_handles_labels()

    # fig.legend(loc='upper left', ncol=1, bbox_to_anchor=(0.8,0.8))
    ax.legend(handles, labels, loc='center left', ncol=1, bbox_to_anchor=(1.2,0.5))
    fig.savefig(os.path.join(out_folder, f"capacity_vs_scarcity.png"))
    plt.clf()

def compare_agents(results, out_folder):
    """
    Plot the comparison between agents when d is fixed
    """
    fig = plt.figure(figsize=(12,8))
    for i, d in enumerate(NUM_EDGES):
        print("D=: ", d)
        ax = plt.subplot(2, 3, i+1)
        for agent_name in results:
            if f"d={d}" in agent_name:
                color = COLORS[AGENT_TYPES.index(get_agent_type(agent_name))]
                xs = range(results[agent_name].shape[1])
                ax.plot(xs, results[agent_name].mean(0), color=color, linewidth=3)
                ax.fill_between(xs, results[agent_name].min(0), results[agent_name].max(0),
                                alpha=0.1, color=color)
                ax.title.set_text(f"d={d}")
                ax.set_xlabel("step")
                ax.set_ylabel("msat-revenue")

    # Set empty plots just for getting a common legend for all subplots
    for name, color in zip(AGENT_TYPES, COLORS):
        ax.plot([], [], color=color, label=name)
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles, labels, loc='center left', ncol=1, bbox_to_anchor=(1.2, 0.5))
    fig.savefig(os.path.join(out_folder, f"Algo_comparison.png"))
    plt.clf()

def compare_best_results(results, out_folder):
    """
    Average each agent results, compare their final revenue values and compare the best between agent types
    """
    max_results_per_agent_type = {agent_type: (-np.inf, np.array([]), None) for agent_type in AGENT_TYPES}
    for agent_name in results:
        agent_type = get_agent_type(agent_name)
        print(agent_name)
        mean_results = results[agent_name].mean(0)
        # compare mean results by last value
        if mean_results[-1] > max_results_per_agent_type[agent_type][0]:
            max_results_per_agent_type[agent_type] = (mean_results[-1], mean_results, agent_name)

    fig = plt.figure(figsize=(12,8))
    ax = plt.subplot(111)
    for agent_type in max_results_per_agent_type:
        _, mean_result, agent_name = max_results_per_agent_type[agent_type]
        ax.plot(range(len(mean_result)), mean_result, label=agent_name, color=COLORS[AGENT_TYPES.index(agent_type)])
    ax.legend(loc='upper center', ncol=2)
    fig.suptitle("Best-results")
    fig.savefig(os.path.join(out_folder, "Best-results.png"))
    plt.clf()


def read_results_and_agent_types(folder_path):
    """
    Plots the pickled results in a folder from old runs
    """
    results = dict()
    for fname in os.listdir(folder_path):
        if fname.endswith(".pkl"):
            agent_name = fname.replace("-results_dict.pkl", "")
            results[agent_name] = pickle.load(open(os.path.join(folder_path, fname), 'rb'))

    return results

if __name__ == '__main__':
    dir_path = "../Experiments/Nodes[50]_Density[50]_IFunds[100.00M]_TAmount[10.00K]_CCost[400.00]_NTransfer[1.00M]"
    all_results = read_results_and_agent_types(dir_path)
    # capacity_vs_scarcity(all_results, dir_path)
    compare_agents(all_results, dir_path)
    # compare_best_results(all_results, dir_path)