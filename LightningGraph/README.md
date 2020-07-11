This module is heavily inspired from ayeletm work in
 https://github.com/ayeletmz/Lightning-Network-Congestion-Attacks.git
 
This module creates Ligtning network status dumps and parses them into a networkx 
graph.

## Basic visatlization
Some basic stats visualization for one of the dumps from ayeletm02:
- edge_capacities: <img src=basic_statistics_figs/edge_capacities.png width="400">
- nodes_total_capacities: <img src=basic_statistics_figs/nodes_total_capacities.png width="400">
- edge_betwenness: <img src=basic_statistics_figs/edge_betwenness.png width="400">
- nodes_routing_types: <img src=basic_statistics_figs/nodes_routing_types.png.png width="400">

Issues:
* Betweeness computation is very slow (100 secs for ~3000 nodes and ~20k edges)

 Todos:
* Add code for dumping Lightning network status and add recent dump
* Alon: add graph structure visualization