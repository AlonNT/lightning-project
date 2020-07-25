import argparse

from utils.graph_helpers import create_sub_graph_by_node_capacity
from LightningGraph.LN_parser import process_lightning_graph
from Agents.Kmeans_agent import find_best_k_nodes


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
