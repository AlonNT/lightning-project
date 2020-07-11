import os
from LN_parser import get_lightning_graph
from matplotlib import pyplot as plt
import networkx as nx
from collections import Counter
def basic_graph_statistics(graph, plot_dir='basic_statistics_figs'):
	# TODO:  rewrite neatly or inspire from seaborn code of ayeletm02
	os.makedirs(plot_dir, exist_ok=True)
	nodes_total_capacities = []
	edge_betwenness = []
	edge_capacities = []
	nodes_routing_types = []
	for node in graph.nodes:
		node  = graph.nodes[node]
		nodes_total_capacities += [node['total_capacity']]
		nodes_routing_types += [node['routing_implemenation']]
	for edge in graph.edges:
		edge = graph.edges[edge]
		edge_betwenness += [edge['betweenness']]
		edge_capacities += [edge['capacity']]

	plt.hist(nodes_total_capacities, label='nodes total capacities', bins = 100)
	plt.ylabel("total capacity")
	plt.legend()
	plt.savefig(os.path.join(plot_dir, "nodes_total_capacities.png"))
	plt.clf()

	plt.hist(edge_betwenness, label='edges betweeness', bins = 100)
	plt.ylabel("weighted betweeness")
	plt.legend()
	plt.savefig(os.path.join(plot_dir, "edge_betwenness.png"))
	plt.clf()

	plt.hist(edge_capacities, label='edges capacities', bins = 100)
	plt.ylabel("capacity")
	plt.legend()
	plt.savefig(os.path.join(plot_dir, "edge_capacities.png"))
	plt.clf()

	count = Counter(nodes_routing_types)
	x_labels, y_labels = zip(*count.items())
	plt.pie(y_labels, labels =x_labels)
	plt.savefig(os.path.join(plot_dir, "nodes_routing_types.png"))
	plt.clf()

if __name__ == '__main__':
	LN_graph = get_lightning_graph('old_dumps/LN_2020.05.13-08.00.01.json', total_capacity=True, infer_imp=True, compute_betweeness=True)
	basic_graph_statistics(LN_graph)