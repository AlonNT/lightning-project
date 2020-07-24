from opt import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY

class GreedyNodeInvestor(object):
    def __init__(self, agent_pub_key, max_edges=10):
        self.balance = 0
        self.default_channel_capacity = 10**6
        self.pub_key = agent_pub_key
        self.added_edges = 0
        self.max_edges=max_edges
        self.nodes_to_connect = None


    def act(self, graph):
        if self.nodes_to_connect is None:
            self.nodes_to_connect = self._find_minimal_capacity_channel_nodes(graph, self.max_edges)
        if self.added_edges < self.max_edges:
            other_node = self.nodes_to_connect[self.added_edges]
            self.added_edges += 1
            p = 0.5
            self.balance -= LN_DEFAULT_CHANNEL_COST + p * self.default_channel_capacity
            command_arguments = {'node1_pub': self.pub_key, 'node2_pub': other_node,
                                 'node1_policy': LND_DEFAULT_POLICY,
                                 'balance_1': p * self.default_channel_capacity,
                                 'balance_2': (1 - p) * self.default_channel_capacity}
            return 'add_edge', list(command_arguments.values())
        return 'NOOP', {}

    def _find_minimal_capacity_channel_nodes(self, graph, num_nodes):
        """Findes nodes with minimal capacity"""
        nodes_set = set()
        edge_keys_to_score = []
        for n1, n2, edge_data in graph.edges(data=True):
            edge_keys_to_score += [(edge_data['capacity'], [n1,n2])]
        edge_keys_to_score = sorted(edge_keys_to_score)
        for item in edge_keys_to_score:
            nodes_set.add(item[1][0])
            nodes_set.add(item[1][1])
            if len(nodes_set) >= num_nodes:
                break

        return list(nodes_set)