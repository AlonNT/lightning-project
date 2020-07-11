This module is heavily inspired from ayeletm work in
 https://github.com/ayeletmz/Lightning-Network-Congestion-Attacks.git
 
This module creates Ligtning network status dumps and parses them into a networkx 
graph.

## Issues:
* Betweeness computation is very slow (100 secs for ~3000 nodes and ~20k edges)

## Todos:
* Add code for dumping Lightning network status and add recent dump
* Alon: add graph structure visualization


## Basic visatlization
Some basic stats visualization for one of the dumps from ayeletm02:
- edge_capacities, nodes_total_capacitie, edge_betwenness

<img src=basic_statistics_figs/edge_capacities.png width="200"> <img src=basic_statistics_figs/nodes_total_capacities.png width="200"> <img src=basic_statistics_figs/edge_betwenness.png width="200">
- nodes_routing_types

<img src=basic_statistics_figs/nodes_routing_types.png width="400">
