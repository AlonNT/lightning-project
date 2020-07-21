import numpy as np
import heapq
import networkx as nx
from typing import Dict, Tuple
from LightningGraph.utils import get_sender_policy_and_id
RISK_FACTOR_BILLIONTHS = 15. / 1000000000


class UpdatablePrioritySet:
    """
    A data-structure that implements a priority set (i.e. min-heap with unique elements).

    We're using the heapq to implement a priority queue, where the key is the return value of given function
        (and we use the object's hash as a tie breaker).
    We extend the functionality of heapq with the `update` function - which remove and re-insert a given object.
    """
    __slots__ = ('set', 'heap')

    def __init__(self):
        # The set to enforce uniqueness.
        self.set = set()

        # The heapq implements a priority queue.
        # The key is the weight of the path starting at this node and ending in 'target'.
        self.heap = list()

    def update(self, node_id, old_weight, new_priority):
        """
        Update an element in the data-structure.
        If it doesn't exist in the data-structure, add it (with the given 'new_priority' as a key).
        If this item already exists in the data-structure, update its key according to the given 'new_priority'.

        :param node_id: The id of the element to update.
        :param old_weight: The old weight of the node. Can be None if the element does not exist yet.
        :param new_priority: The new priority for the given element.
        """
        if node_id in self.set:  # avg: O(1), worst: O(log n)
            try:
                self.heap.remove((old_weight, node_id))  # O(n)
            except ValueError:
                # we didn't updated it in the previous time because it's too deep, so it's not in the list
                pass
        else:
            self.set.add(node_id)  # avg: O(1), worst: O(log n)

        # TODO Don't we need to brake ties in some (preferably deterministic) way, like the hash used in Saar's code?
        # TODO Make sure the tie braking happens, using this data-structure with toy elements.
        heapq.heappush(self.heap, (new_priority, node_id))  # O(log n)

    def pop(self):
        """
        :return: The item with the minimal key from data-structure (and this item is removed from the data-structure).
        """
        r = heapq.heappop(self.heap)[1]  # O(1)
        self.set.remove(r)  # avg: O(1), worst: O(log n)
        return r

    def is_empty(self):
        """
        :return: True if and only if the data-structure is empty.
        """
        return len(self.set) == 0


def lnd_weight(policy: Dict[str, int], amount: int, prev_weight: int) -> Tuple[int, int]:
    """
    Denote by 'node1' the node that needs to transfer money to 'node2' which he is connected by a direct channel.
    This looks like: source ------> ... ---a---> node1 ---b---> node2 ------> ... ------> target
    Note that 'a' is the amount of money node1 needs to receive in order to transfer 'b' amount of money to node2,
    (and node2 might be transferring this money forwards).
    The amount node2 is supposed to get is 'amount' (a.k.a. 'b'),
    and the amount node1 needs to receive is amount + fee (a.k.a. 'a'),
    where the fee is calculated according to node1's policy.

    So this function gets the policy of the node1, the amount of money node2 needs to get,
    and the weight of the route continuing from node2 to the final target node.
    It calculates the weight of the path starting from node1 and continuing further to the path
    starting at node2 with weight 'prev_weight', as well as the amount of money node1 needs to get
    for this transaction to be possible.

    :param policy: The policy of node1 which is transferring the money to node2 (which he might forward it later).
                   It states the base-fee, proportional-fee and time-lock-delta.
    :param amount: The amount of money to be transferred from node1 to node2.
                   Note that this amount includes the fees that need to be paid for the later channels in the route.
    :param prev_weight: The weight of the path from node2 to the target node.

    :return: A tuple containing two integers:
                 (1) The amount of money node1 needs to receive for transferring the money forwards.
                 (2) The weight of the route starting at node1 and reaching 'target' eventually.
    """
    fee_base = policy['fee_base_msat']
    fee_proportional = policy['fee_rate_milli_msat']
    delay = policy['time_lock_delta']
    fee = round(fee_base + (amount * fee_proportional))                          # TODO Is it ok to round to int?
    weight = round(prev_weight + amount * delay * RISK_FACTOR_BILLIONTHS + fee)  # TODO Is it ok to round to int?
    return amount + fee, weight


def get_route(graph: nx.MultiGraph, source_id, target_id, amount: int, max_hops: int = 20):
    """
    Given a target node and a list of nodes, compute the route from any node in the list to the target node.
    The route is calculated 'backwards-Dijkstra' - from the target node until each one of the nodes.

    :param graph: The graph describing the network.
    :param source_id: The source node.
    :param target_id: The target node.
    :param amount: Amount (in milli-satoshis) to transfer.
                   Note that this is the amount of money that should reach the target node eventually,
                   and more money will be added in order to pay the fees on the route.
    :param max_hops: Maximal number of intermediate nodes in the route.

    :return: A triplet representing the selected route:
                 (1) The path starting from this node to the target node (a list of Nodes).
                 (2) The amount of money that this node receive (and transfer forwards).
                 (3) The weight of the path.
    """
    # Initialize the 'amount_node_needs' and 'weight' attributes of each node as INFINITY.
    # These values will be changed during the run of the routing algorithm.
    nx.set_node_attributes(graph, np.inf, 'amount_node_needs')
    nx.set_node_attributes(graph, np.inf, 'weight')

    # Initialize 'path_to_target' for each node in the graph - it's a list containing the path from it to 'target'.
    # Note that we can't use set_node_attributes with mutable types like a list
    # (as this list will be shared among all nodes which is undesirable).
    for node in graph.nodes:
        graph.nodes[node]['path_to_target'] = list()

    unvisited_nodes = UpdatablePrioritySet()

    # Initialize the target attributes with its desired values.
    graph.nodes[target_id]['amount_node_needs'] = amount  # The amount 'target' needs to get is the given 'amount'.
    graph.nodes[target_id]['weight'] = 0                  # The weight of the path starting and ending in 'target' is 0.

    # Add the target node to the unvisited_nodes data-structure with weight 0.
    unvisited_nodes.update(target_id, None, 0)

    # Iterate as long as there is some unvisited nodes we need to visit.
    while not unvisited_nodes.is_empty():

        # Extract the node in the unvisited_nodes data-structure
        # that has a path starting from it and ending in 'target'  with a minimal weight.
        # This node will be a 'receiver' of money that it needs to transfer further to 'target',
        # that's why it's named 'receiver_node'.
        receiver_node_id = unvisited_nodes.pop()

        # If the receiver node is the source node, we can finish and return the path it has,
        # because we know this path is the path with minimal weight among all paths
        # that start in 'source' and end in 'target'.
        if receiver_node_id == source_id:
            return (graph.nodes[source_id]['path_to_target'],
                    graph.nodes[source_id]['weight'],
                    graph.nodes[source_id]['amount_node_needs'])

        # Go over all the neighbors of this receiver node, and for each one the weight in the heap might need updating.
        receiver_node_edges = graph.edges(receiver_node_id, data=True)
        for _, _, edge_data in receiver_node_edges:
            sender_node_policy, sender_node_id = get_sender_policy_and_id(receiver_node_id, edge_data)
            edge_key = (sender_node_id, receiver_node_id, edge_data['channel_id']) # TODO: order does matter here doesn't it?

            # Calculate the weight of the path starting at 'sender' and ending at 'target',
            # passing first through the current 'receiver' (and continuing to target from there).
            # The amount that 'sender' needs to get in order to perform this multi-hop transfer is also calculated.
            amount_sender_needs, weight = lnd_weight(sender_node_policy,
                                                     amount=graph.nodes[receiver_node_id]['amount_node_needs'],
                                                     prev_weight=graph.nodes[receiver_node_id]['weight'])

            sender_node_data = graph.nodes[sender_node_id]
            receiver_node_data = graph.nodes[receiver_node_id]

            # If the weight of the path starting at the neighbor and passing through the receiver_node is lower than
            # the current weight of the path that is saved for the neighbor.
            if weight < sender_node_data['weight']:
                # Update the weight of the path in the heap accordingly, since it's lower.
                # Do not add to the unvisited nodes data-structure the new path if it's too long.
                # Minus 1 because path is a list of edges and not a list of nodes, and #edges = #nodes + 1.
                if len(receiver_node_data['path_to_target']) < max_hops - 1:
                    unvisited_nodes.update(sender_node_id, sender_node_data['weight'], new_priority=weight)

                # Update the attributes of the node in the graph itself, to use in later iterations.
                sender_node_data['weight'] = weight
                sender_node_data['amount_node_needs'] = amount_sender_needs
                sender_node_data['path_to_target'] = [edge_key] + receiver_node_data['path_to_target']

    return None  # No route was found transferring 'amount; from 'source' to 'target'.
