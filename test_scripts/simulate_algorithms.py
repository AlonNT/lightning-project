from Enviroments.lightning_enviroment import LightningEniroment
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.common import human_format
from copy import deepcopy
import numpy as np
from collections import defaultdict
from Agents.random_agent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from Agents.greedy_agent import GreedyNodeInvestor
from time import time

MAX_AGENT_FUNDS = 1000000
NUM_TRANSACTIONS=100
REPEAT_SIMULATION = 10
ENVIROMENT_NUM_NODES=500
ENIROMENT_DENSITY=100
ENVIROMENT_TRANSFERS_MAX_AMOUNT=10**6

def get_env():

    graph = create_sub_graph_by_node_capacity(k=ENVIROMENT_NUM_NODES,
                                              highest_capacity_offset=ENIROMENT_DENSITY)

    env = LightningEniroment(graph, tranfers_per_step=NUM_TRANSACTIONS,
                             transfer_max_amount=ENVIROMENT_TRANSFERS_MAX_AMOUNT)
    return env

def run_experiment(agent_constructors):

    """
    1. Creates a common Lightning enviroment
    for each agent:
    2.      Ask agent for edges he want to establish given a funds constraint
    3.      add edges to a copy of the enviroment
    4       repeat simulation of so many transaction and average final balance
    param: agent_constructors: list of tuples of an agent constructor and additional Kwargs
    """
    # Create the base enviroment whos copies will run all simulations
    env = get_env()
    new_node_pub_key = env.create_agent_node()

    results = defaultdict(list)
    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class heriting AbstractAgent
        agent = agent_constructor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS, **kwargs)
        print("Agent:", agent.name)
        for repeat in range(REPEAT_SIMULATION):
            env = deepcopy(env)

            # ask agent for edges to add
            new_edges = agent.get_channels(env.get_state()) # state is just the graph

            # add edges to a local copy of the enviroment
            for edge in new_edges:
                env._add_edge(**edge)

            start = time()
            env.step() # peforms NUM_TRANSACTIONS transactions
            print(f"\t{repeat} {human_format(NUM_TRANSACTIONS/(time()-start))} tnx/sec")

            # report revenue
            agent_balance = env.get_node_balance(new_node_pub_key) - MAX_AGENT_FUNDS
            results[agent.name] += [agent_balance]

    print(f"Score over {REPEAT_SIMULATION} simulations of {NUM_TRANSACTIONS} transactions")
    for agent_name in results:
        print(f"mean: {human_format(np.mean(results[agent_name]))}, std: {np.mean(np.std(results[agent_name]))}")


if __name__ == '__main__':
    args = [(RandomInvestor, {}), (GreedyNodeInvestor, {})]
    run_experiment(args)
