import random

class random_investor(object):
    def __init__(self, network_enviroment, max_nodes=1):
        self.network_enviroment = network_enviroment
        self.balance = 0
        self.max_nodes = max_nodes
        self.default_channel_capacity = 10

        pub_key = self.network_enviromen.create_agent_node()
        self.my_pub_key = pub_key

    def act(self):
        random_node_pubkey = random.choise(self.network_enviroment.graph.nodes)
        random_node = self.network_enviroment.graph.nodes[random_node_pubkey]
        self.balance -= self.default_channel_capacity
        self.network_enviroment.add_edge(self.pub_key, random_node, self.default_channel_capacity)

    def print_balance(self):
        return self.balance + self.network_enviroment.get_node_balance(self.my_pub_key)
