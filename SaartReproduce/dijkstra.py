from SaartReproduce.classes import Node, Channel
from typing import List, Dict, Tuple, Callable, TypeVar, Generic
import heapq
BIG = 999_999_999_999_999
T = TypeVar('T')

class Dijkstra_info:
    __slots__ = ('node', 'total', 'weight', 'path', 'final_path', 'depth')

    def __init__(self, node: 'Node', total=BIG, weight=BIG, path=None, depth=None):
        self.node = node
        self.total: int = total
        self.weight: float = weight
        self.path: List[Node] = path or []
        self.final_path: List[Node] = []
        self.depth: int = depth

    def get(self):
        return self

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

    def __bool__(self):
        return bool(self.set)


def update_single(dijkstra: Dijkstra_info, channel: Channel, to_visit: UpdatablePrioritySet[Dijkstra_info], get_weight, max_hops):
    amount_plus_fee, time_lock_penalty = get_weight(channel, amount=dijkstra.total, prev_weight=dijkstra.weight)
    other_dijkstra: Dijkstra_info = channel.other_node(dijkstra.node).dijkstra_info.get()
    if time_lock_penalty < other_dijkstra.weight:
        if dijkstra.node in dijkstra.path:
            return  # we found a loop.
        if dijkstra.depth != max_hops:
            to_visit.update(other_dijkstra, other_dijkstra.weight, time_lock_penalty)
        other_dijkstra.total = amount_plus_fee
        other_dijkstra.path = dijkstra.path + [dijkstra.node]
        other_dijkstra.weight = time_lock_penalty
        other_dijkstra.depth = dijkstra.depth + 1


def find_route(nodes: List[Node], dst: Node, get_weight, msat, max_hops, src=None) -> Dict[Node, List[Tuple[List[Node], float, float]]]:
    for node in nodes:
        node.dijkstra_info = Dijkstra_info(node)

    dst_worst_dijkstra = dst.dijkstra_info.get()
    dst_worst_dijkstra.total = msat
    dst_worst_dijkstra.weight = 0
    dst_worst_dijkstra.depth = 0

    to_visit: UpdatablePrioritySet[Dijkstra_info] = UpdatablePrioritySet(lambda d: d.weight)
    to_visit.update(dst_worst_dijkstra, 0, 0) # add dest node to the unvisited list
    while to_visit:
        dijkstra: Dijkstra_info = to_visit.pop()

        for channel in dijkstra.node.channels: # search for incoming channels
            if dijkstra.node == channel.node2:
                update_single(dijkstra, channel, to_visit, get_weight, max_hops)

    res = {}
    for n in nodes :
        if n.name != dst.name:
            if n.dijkstra_info.path:
                path = (n.dijkstra_info.path + [n])[::-1]
                res[n] = [(path, n.dijkstra_info.total, n.dijkstra_info.weight)]
    return res
