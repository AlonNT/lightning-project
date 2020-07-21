from garbage.SaartReproduce.classes import Node, Channel
from typing import List, Dict, Tuple, Callable, TypeVar, Generic
import heapq
INFINITY_INT = 999_999_999_999_999
T = TypeVar('T')


class DijkstraInfo:
    __slots__ = ('node', 'total', 'weight', 'path', 'final_path', 'depth')

    def __init__(self, node: 'Node', total=INFINITY_INT, weight=INFINITY_INT, path=None, depth=None):
        self.node = node
        self.total: int = total
        self.weight: float = weight
        self.path: List[Node] = path or []
        self.final_path: List[Node] = []
        self.depth: int = depth


class UpdatablePrioritySet(Generic[T]):
    """
    We're using the set to enforce uniqueness.
    We're using the heapq to implement a priority queue, where the key is the return value of given function
        (and we use the object's hash as a tie breaker).
    We extend the functionality of heapq with the `update` function - which remove and re-insert a given object.
    """
    __slots__ = ('set', 'heap', 'get_priority')

    def __init__(self, get_priority: Callable[[T], float]):
        self.set = set()
        self.heap = []
        self.get_priority = get_priority

    def update(self, i: T, old_priority, new_priority):
        if i in self.set:  # avg: O(1), worst: O(log n)
            try:
                self.heap.remove((old_priority, hash(i), i))  # O(n)
            except ValueError:
                # we didn't updated it in the previous time because it's too deep, so it's not in the list
                pass
        else:
            self.set.add(i)  # avg: O(1), worst: O(log n)
        heapq.heappush(self.heap, (new_priority, hash(i), i))  # O(log n)

    def pop(self) -> T:
        r = heapq.heappop(self.heap)[2]  # O(1)
        self.set.remove(r)  # avg: O(1), worst: O(log n)
        return r

    def is_empty(self):
        return len(self.set) == 0

    def __bool__(self):
        return bool(self.set)

    def __len__(self):
        return len(self.set)


def update_single(dijkstra_info: DijkstraInfo, channel: Channel, nodes_to_visit: UpdatablePrioritySet[DijkstraInfo],
                  get_weight, max_hops):
    """
    Update the nodes_to_visit data-structure and the other-node's DijkstraInfo
    according to the given DijkstraInfo of the first node in the path and its channel.
    TODO [to Ariel] Did I understand it correctly? Anything else is being updated?

    :param dijkstra_info:
    :param channel:
    :param nodes_to_visit:
    :param get_weight:
    :param max_hops:
    """
    amount_plus_fee, time_lock_penalty = get_weight(channel,
                                                    amount=dijkstra_info.total,
                                                    prev_weight=dijkstra_info.weight)
    other_dijkstra: DijkstraInfo = channel.other_node(dijkstra_info.node).dijkstra_info
    if time_lock_penalty < other_dijkstra.weight:
        if dijkstra_info.node in dijkstra_info.path:
            return  # we found a loop.
        if dijkstra_info.depth != max_hops:
            nodes_to_visit.update(other_dijkstra, other_dijkstra.weight, time_lock_penalty)
        other_dijkstra.total = amount_plus_fee
        other_dijkstra.path = dijkstra_info.path + [dijkstra_info.node]
        other_dijkstra.weight = time_lock_penalty
        other_dijkstra.depth = dijkstra_info.depth + 1


def find_route(nodes: List[Node], target: Node,
               get_weight, msat, max_hops) -> Dict[Node, Tuple[List[Node], float, float]]:
    """
    Given a target node and a list of nodes, compute the route from any node in the list to the target node.
    The route is calculated 'backwards-Dijkstra' - from the target node until each one of the nodes.

    :param nodes: A list of nodes which are potentially source nodes.
    :param target: The target node.
    :param get_weight: The weight function (can be the one used in LND, C_Lightning or Eclair).
    :param msat: Amount (in milli-satoshis) to transfer.
                 Note that this is the amount of money that should reach the target node eventually,
                 and more money will be added in order rto pay the fees on the route.
    :param max_hops: Maximal number of intermediate nodes in the route.

    :return: A dictionary mapping each node to a triplet representing the selected route.
             The triplet contains:
                 (1) The path starting from this node to the target node (a list of Nodes).
                 (2) The amount of money that this node receive (and transfer forwards). TODO [to Ariel] verify me.
                 (3) The weight of the path.
    """
    # Initialize the DijkstraInfo class of each node with the initial values (infinity weight & amount, etc).
    for node in nodes:
        node.dijkstra_info = DijkstraInfo(node)

    # Initialize the target DijkstraInfo with its desired values.
    target.dijkstra_info.total = msat  # The total amount of money that 'target' has to get is the given 'msat'.
    target.dijkstra_info.weight = 0    # The weight of the (empty) path starting and ending in 'target' is 0.
    target.dijkstra_info.depth = 0     # The depth of the path is 0 (since it's and empty path).

    # Initialize the UpdatablePrioritySet, where the the priority of each element is the weight of the path.
    nodes_to_visit: UpdatablePrioritySet[DijkstraInfo] = UpdatablePrioritySet(lambda d: d.weight)

    # Add the target node to the nodes to visit, with priority (i.e. weight) of 0.
    nodes_to_visit.update(target.dijkstra_info, 0, 0)

    # Iterate as long as there is some nodes we need to visit.
    while not nodes_to_visit.is_empty():
        dijkstra_info: DijkstraInfo = nodes_to_visit.pop()

        # Search for incoming channels, and update the 'nodes_to_visit' data structure accordingly.
        for channel in dijkstra_info.node.channels:
            if dijkstra_info.node == channel.node2:
                update_single(dijkstra_info, channel, nodes_to_visit, get_weight, max_hops)

    result = dict()
    for node in nodes:
        # TODO [to Ariel] if node != target then node.dijkstra_info.path is necessarily not empty, right?
        if (node.name == target.name) or len(node.dijkstra_info.path) == 0:
            continue

        # TODO why build the path in a reverse order and then reverse it? :-O
        path = (node.dijkstra_info.path + [node])[::-1]

        # TODO why hold a list containing a single tuple? why not just a tuple? :-O
        result[node] = (path, node.dijkstra_info.total, node.dijkstra_info.weight)

    return result
