import random

DEFAULT_CHANNEL_COST = 1

class random_investor(object):
    def __init__(self, agent_pub_key, max_nodes=1):
        self.balance = 0
        self.max_nodes = max_nodes
        self.default_channel_capacity = 10
        self.pub_key = agent_pub_key

    def act(self, graph):
        if random.random() < 0.5:
            random_node_pub_key = random.choice(graph.graph.nodes)
            self.balance -= DEFAULT_CHANNEL_COST
            p = random.random()
            command_arguments = {'pub_key_1': self.pub_key, 'pub_key_2': random_node_pub_key,
                                 'balance_1':p*self.default_channel_capacity, 'balance_2':(1-p)*self.default_channel_capacity}
            return 'add_edge', list(command_arguments.values())
        else:
            return 'NOOP', {}
