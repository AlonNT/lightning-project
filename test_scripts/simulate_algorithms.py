import numpy as np
import networkx as nx
import consts
from typing import Optional
from Enviroments.lightning_enviroment import LightningEnvironment
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.common import human_format
from copy import deepcopy
from collections import defaultdict
from Agents.random_agent import RandomInvestor
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from Agents.greedy_agent import GreedyNodeInvestor
from utils.loggers import Logger
from time import time

MAX_AGENT_FUNDS = 1000000
NUM_TRANSACTIONS = 100
REPEAT_SIMULATION = 10
ENVIRONMENT_NUM_NODES = 500
ENVIRONMENT_DENSITY = 100
ENVIRONMENT_TRANSFERS_MAX_AMOUNT = 10 ** 6


def get_env() -> nx.MultiGraph:
    graph = create_sub_graph_by_node_capacity(k=ENVIRONMENT_NUM_NODES,
                                              highest_capacity_offset=ENVIRONMENT_DENSITY)

    env = LightningEnvironment(graph, transfers_per_step=NUM_TRANSACTIONS,
                               transfer_max_amount=ENVIRONMENT_TRANSFERS_MAX_AMOUNT)
    return env


def get_logger(log_dir) -> Optional[Logger]:
    """
    :param log_dir: The path to output the logs.
    :return: None if consts.SIMULATION_LOG_DIR is None, and a relevant Logger instance otherwise.
    """
    if consts.SIMULATION_LOG_DIR is None:
        return None

    return Logger(consts.SIMULATION_LOG_FREQ, log_dir)


def run_experiment(agent_constructors, out_dir: Optional[str] = None):
    """
    1. Creates a common Lightning environment
    for each agent:
    2. Ask agent for edges he want to establish given a funds constraint
    3. Add edges to a copy of the enviroment
    4. Repeat simulation of so many transaction and average final balance
    param: agent_constructors: list of tuples of an agent constructor and additional Kwargs
    """
    # Create the base environment who's copies will run all simulations
    env = get_env()
    new_node_pub_key = env.create_agent_node()

    results = defaultdict(list)
    for (agent_constructor, kwargs) in agent_constructors:
        # Create agent: A get_edges callable, an instance of a class heriting AbstractAgent
        agent = agent_constructor(new_node_pub_key, initial_funds=MAX_AGENT_FUNDS, **kwargs)
        # Use the Logger for ploting the reward of each agent
        simulation_logger: Logger = get_logger(out_dir)

        print("Agent:", agent.name)
        for repeat in range(REPEAT_SIMULATION):
            env = deepcopy(env)

            # Ask agent for edges to add
            new_edges = agent.get_channels(env.get_state())  # state is just the graph

            # Add edges to a local copy of the environment
            for edge in new_edges:
                env._add_edge(**edge)

            start = time()
            env.step()  # preforms NUM_TRANSACTIONS transactions
            print(f"\t{repeat} {human_format(NUM_TRANSACTIONS/(time()-start))} tnx/sec")

            # report revenue
            agent_balance = env.get_node_balance(new_node_pub_key) - MAX_AGENT_FUNDS
            results[agent.name] += [agent_balance]

            simulation_logger.log_step(agent_balance)

    print(f"Score over {REPEAT_SIMULATION} simulations of {NUM_TRANSACTIONS} transactions")
    for agent_name in results:
        print(
            f"{agent_name}: mean: {human_format(np.mean(results[agent_name]))}, std: {np.mean(np.std(results[agent_name]))}")


if __name__ == '__main__':
    args = [(RandomInvestor, {}), (GreedyNodeInvestor, {}), (LightningPlusPlusAgent, {'alpha': 2})]
    run_experiment(args, out_dir=consts.SIMULATION_OUT_DIR)
