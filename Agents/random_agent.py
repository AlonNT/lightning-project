import random
from opt import LN_DEFAULT_CHANNEL_COST, LND_DEFAULT_POLICY

class RandomInvestor(object):
    def __init__(self, agent_pub_key, max_edges=10):
        self.balance = 0
        self.default_channel_capacity = 10**6
        self.pub_key = agent_pub_key
        self.added_edges = 0
        self.max_edges=max_edges

    def act(self, graph):
        if self.added_edges < self.max_edges and random.random() < 0.3:
            random_node_pub_key = random.choice(list(graph.nodes))
            while random_node_pub_key == self.pub_key:
                random_node_pub_key = random.choice(list(graph.nodes))
            p = random.random()
            self.balance -= LN_DEFAULT_CHANNEL_COST +  p * self.default_channel_capacity
            command_arguments = {'node1_pub': self.pub_key, 'node2_pub': random_node_pub_key,
                                 'node1_policy':LND_DEFAULT_POLICY,
                                 'node1_balance': p * self.default_channel_capacity,
                                 'node2_balance_2': (1 - p) * self.default_channel_capacity}
            self.added_edges += 1
            return 'add_edge', list(command_arguments.values())
        else:
            return 'NOOP', {}
