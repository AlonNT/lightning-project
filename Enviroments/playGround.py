import networkx as nx


g = nx.MultiGraph()
g.add_node(1)
g.add_node(2)
g.add_node(3)

g.add_edge(1, 2, cap=2)
g.add_edge(1, 3, cap=5)

edges = g.edges(nbunch=1, data=True)





