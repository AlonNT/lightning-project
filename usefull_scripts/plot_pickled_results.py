from utils.visualizers import plot_experiment_mean_and_std
import os
import pickle
import matplotlib.pyplot as plt


def read_from_directory(folder_path):
    """
    Plots the pickled results in a folder from old runs
    """
    results = dict()
    for fname in os.listdir(folder_path):
        if fname.endswith(".pkl") and "d=16" in fname:
            agent_name = fname.replace("-results_dict.pkl", "")
            results[agent_name] = pickle.load(open(os.path.join(folder_path, fname), 'rb'))

    fig, ax = plot_experiment_mean_and_std(results)
    fig.suptitle(os.path.basename(folder_path))
    fig.savefig(os.path.join(folder_path, "Simulator_log_4.png"))
    plt.show()

if __name__ == '__main__':
    read_from_directory("../Experiments/Nodes[50]_Density[50]_IFunds[100.00M]_TAmount[10.00K]_CCost[400.00]_NTransfer[1.00M]")