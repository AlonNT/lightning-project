import networkx as nx
import matplotlib.pyplot as plt
import argparse
from routing.route_selection import get_route

dispatcher = {
    'complete_graph': nx.complete_graph,
    'binomial_tree': nx.binomial_tree,
    'cycle_graph': nx.cycle_graph,
    'ladder_graph': nx.ladder_graph,
    'star_graph': nx.star_graph,
    'wheel_graph': nx.wheel_graph
}


def get_graph(graph_type: str, n: int) -> nx.Graph:
    if graph_type not in dispatcher:
        raise ValueError('graph_type {} is not in the dispatcher.'.format(graph_type))

    graph: nx.Graph = dispatcher[graph_type](n)

    return graph


def draw_graph(graph: nx.Graph):
    plt.figure()
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()


def parse_args():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument('graph_type', type=str,
                        help='Which graph to draw. Should be a string that exists in the dispatcher dictionary')
    parser.add_argument('n', type=int,
                        help='Parameter for the graph generator '
                             '(usually it\'s the number of vertices or something related to that).')

    return parser.parse_args()


def main():
    args = parse_args()
    graph = get_graph(args.graph_type, args.n)
    draw_graph(graph)
    stop = 'here'
    # get_route()


if __name__ == '__main__':
    main()
