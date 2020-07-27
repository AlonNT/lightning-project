from Enviroments.lightning_enviroment import LightningEniroment
from utils.graph_helpers import create_sub_graph_by_node_capacity
from copy import deepcopy
import numpy as np
from collections import defaultdict
from Agents.random_agent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from Agents.greedy_agent import GreedyNodeInvestor

MAX_AGENT_FUNDS = 100000
NUM_TRANSACTIONS=1000
REPEAT_SIMULATION = 3
ENVIROMENT_NUM_NODES=20
ENIROMENT_DENSITY=100
ENVIROMENT_TRANSFERS_MAX_AMOUNT=10**6

def get_env():
    graph = create_sub_graph_by_node_capacity(k=ENVIROMENT_NUM_NODES,
                                              highest_capacity_offset=ENIROMENT_DENSITY)

    env = LightningEniroment(graph, tranfers_per_step=NUM_TRANSACTIONS,
                             transfer_max_amount=ENVIROMENT_TRANSFERS_MAX_AMOUNT)
    return env

def run_experiment(agent_constructors):
    # Create the base enviroment whos copies will run all simulations
    env = get_env()
    new_node_pub_key = env.create_agent_node()

    results = defaultdict(list)
    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable
        agent = agent_constructor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS, **kwargs)
        # agent = RandomInvestor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS)
        print("Agent:", agent.name)
        for repeat in range(REPEAT_SIMULATION):
            env = deepcopy(env)
            new_edges = agent.get_channels(env.get_state()) # state is just the graph

            print(f"\t{repeat} Adding edges to graph")
            for edge in new_edges:
                env._add_edge(**edge)
            print(f"\t{repeat} Performing transactions")
            env.step() # peforms NUM_TRANSACTIONS transactions
            agent_balance = env.get_node_balance(new_node_pub_key) - MAX_AGENT_FUNDS
            results[agent.name] += [agent_balance]

    print(f"Score over {REPEAT_SIMULATION} simulations of {NUM_TRANSACTIONS} transactions")
    for agent_name in results:
        print(f"mean: {np.mean(results[agent_name])}, std: {np.std(results[agent_name])}")


if __name__ == '__main__':
    args = [(RandomInvestor, {}), (GreedyNodeInvestor, {})]
    run_experiment(args)
