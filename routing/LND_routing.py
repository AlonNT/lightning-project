import numpy as np
import heapq
import networkx as nx
from routing.utils import nodes_list_to_edges
RiskFactorBillionths = 15. / 1000000000


class UpdatablePrioritySet:
    """
    We're using the set to enforce uniqueness.
    We're using the heapq to implement a priority queue, where the key is the return value of given function
        (and we use the object's hash as a tie breaker).
    We extend the functionality of heapq with the `update` function - which remove and re-insert a given object.
    """
    __slots__ = ('set', 'heap')

    def __init__(self):
        self.set = set()
        self.heap = []

    def update(self, node_id, old_weight,  new_priority):
        if node_id in self.set:  # avg: O(1), worst: O(log n)
            try:
                self.heap.remove((old_weight, node_id))  # O(n)
            except ValueError:
                # we didn't updated it in the previous time because it's too deep, so it's not in the list
                pass
        else:
            self.set.add(node_id)  # avg: O(1), worst: O(log n)
        heapq.heappush(self.heap, (new_priority, node_id))  # O(log n)

    def pop(self):
        r = heapq.heappop(self.heap)[1]  # O(1)
        self.set.remove(r)  # avg: O(1), worst: O(log n)
        return r

    def is_empty(self):
        return len(self.set) == 0

def lnd_weight(transaction_policy, amount, prev_weight):
    fee_base = transaction_policy['fee_base_msat']
    fee_prop = transaction_policy['fee_rate_milli_msat']/1000
    delay = transaction_policy['time_lock_delta']
    fee = fee_base + (amount * fee_prop)
    time_lock_penalty = prev_weight + amount * delay * RiskFactorBillionths + fee
    return amount + fee, time_lock_penalty

def get_policy_and_other_node(node_id, edge):
    if node_id == edge['node1_pub']:
        fee_policy = edge['node1_policy']  # TODO: Do we need to use the other node's policy  here?
        other_node_id = edge['node2_pub']
    elif node_id == edge['node2_pub']:
        fee_policy = edge['node2_policy']
        other_node_id = edge['node1_pub']
    else:
        raise Exception("Bad edge")
    return fee_policy, other_node_id

def get_route(graph, source_id, target_id, amount):
    ## Preprocess:
    nx.set_node_attributes(graph, np.inf, 'dijkstra_total')
    nx.set_node_attributes(graph, np.inf, 'weight')
    for node_id in graph.nodes: #  can't use set_node_attributes with mutable types like []
        graph.nodes[node_id]['path_to_target'] = []


    # Dijkstra:
    heap = UpdatablePrioritySet()
    graph.nodes[target_id]['dijkstra_total'] = amount
    graph.nodes[target_id]['weight'] = 0
    heap.update(target_id, None, 0)

    while not heap.is_empty():
        node_id = heap.pop()
        if node_id == source_id:
            path_nodes = graph.nodes[source_id]['path_to_target']
            return nodes_list_to_edges(graph, path_nodes) # TODO: Coonsider saving edges instead of nodes in the first place?
            # Todo:  consider returning (or using the filled attributes) dijkstra_total and weight of nodes in path to facilitate actual transfer
        node_edges = graph.edges(node_id, data=True)
        for edge in node_edges:
            edge_data = edge[2]
            fee_policy, other_node_id = get_policy_and_other_node(node_id, edge_data)

            amount_plus_fee, weight = lnd_weight(fee_policy, amount=graph.nodes[node_id]['dijkstra_total'], prev_weight=graph.nodes[node_id]['weight'])

            if weight < graph.nodes[other_node_id]['weight']:
                heap.update(other_node_id, graph.nodes[other_node_id]['weight'], new_priority=weight)
                graph.nodes[other_node_id]['weight'] = weight
                graph.nodes[other_node_id]['dijkstra_total'] = amount_plus_fee
                graph.nodes[other_node_id]['path_to_target'] = graph.nodes[node_id]['path_to_target'] + [node_id]

    return None
