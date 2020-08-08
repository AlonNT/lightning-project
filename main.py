import os
from typing import Tuple, Union, Optional

import numpy as np

import consts
from Agents.LightningPlusPlusAgent import LightningPlusPlusAgent
from Agents.greedy_agent import GreedyNodeInvestor
from Agents.random_agent import RandomInvestor
from LigtningSimulator.LightningSimulator import LightningSimulator
from utils.graph_helpers import create_sub_graph_by_node_capacity
from utils.loggers import Logger
from utils.visualizers import create_simulation_gif, compare_simulation_logs

Agent = Union[RandomInvestor, GreedyNodeInvestor, LightningPlusPlusAgent]


def get_environment_and_agent(agent_type: str) -> Tuple[LightningSimulator, Agent]:
    """
    Gets the agent type created an environment and an agent in that environment.

    :param agent_type: Should be Naive, Greedy or LPP.
                       This corresponds to the different agents types one can use.
    :return: a tuple containing two elements - the first is the environment and the second is the agent.
    """
    graph = create_sub_graph_by_node_capacity(k=consts.ENVIRONMENT_NUM_NODES,
                                              highest_capacity_offset=consts.ENVIRONMENT_DENSITY)
    env = LightningSimulator(graph,
                             transfers_per_step=consts.ENVIRONMENT_TRANSFERS_PER_STEP,
                             transfer_max_amount=consts.ENVIRONMENT_TRANSFERS_MAX_AMOUNT)
    agent_pub_key = env.create_agent_node()

    if agent_type == "Naive":
        agent = RandomInvestor(agent_pub_key, initial_funds=consts.AGENT_MAX_FUNDS)
    elif agent_type == "Greedy":
        agent = GreedyNodeInvestor(agent_pub_key, initial_funds=consts.AGENT_MAX_FUNDS)
    elif agent_type == "LPP":
        agent = LightningPlusPlusAgent(agent_pub_key, initial_funds=consts.AGENT_MAX_FUNDS)
    else:
        raise ValueError(f"Unsupported agent: {agent_type}")

    return env, agent


def get_agent_reward(env: LightningSimulator, agent: Agent) -> int:
    """
    Return the reward of the given agent in the given environment,
    which is the current balance he owns minus his initial funds.

    :param env: The environment where the agent operate in.
    :param agent: The agent to query his reward.
    :return: The reward of the agent.
    """
    return env.get_node_balance(agent.pub_key) - consts.AGENT_MAX_FUNDS


def get_logger(log_dir) -> Optional[Logger]:
    """
    :param log_dir: The path to output the logs.
    :return: None if consts.SIMULATION_LOG_DIR is None, and a relevant Logger instance otherwise.
    """
    if consts.SIMULATION_LOG_DIR is None:
        return None

    return Logger(consts.SIMULATION_LOG_FREQ, log_dir)


def simulate_one_episode(env: LightningSimulator, agent: Agent, num_steps: int,
                         simulation_logger: Optional[Logger] = None, out_dir: Optional[str] = None) -> int:
    """
    Simulate a single episode of the given agent in the given environment.

    :param env: The environment to simulate on.
    :param agent: The agent to simulate.
    :param num_steps: The total number of steps of the simulation.
    :param simulation_logger: The logger of the simulation. If it's None then nothing is being logged.
    :param out_dir: The output directory to dump images describing the simulation.

    :return: The final reward of the agent - the episode score.
    """
    print("Simulating one episode...")

    state = env.get_graph()
    agent_reward = 0

    for step in range(num_steps):
        agent_reward = get_agent_reward(env, agent)

        if simulation_logger is not None:
            simulation_logger.log_step(agent_reward)

        if out_dir is not None:
            env.render(out_dir=os.path.join(out_dir, "frames", f"step-%s" % str(step).zfill(3)),
                       agent_reward=agent_reward)

        action = agent.act(state)
        new_state = env.run(action)
        state = new_state

    if out_dir is not None:
        create_simulation_gif(os.path.join(out_dir, "frames"))
    if simulation_logger is not None:
        simulation_logger.pickle_episode_scores()

    return agent_reward


def evaluate_agents(num_simulations: int, steps_per_simulation: int):
    """
    Average simulations final balances for all each agents and compare them, printing the final results.

    :param num_simulations: Number of simulations to perform on each agent.
    :param steps_per_simulation: Number of steps per simulation.
    """
    agents_names = ["Naive", "Greedy"]
    all_scores = {name: list() for name in agents_names}
    for agent_name in agents_names:
        for _ in range(num_simulations):
            env, agent = get_environment_and_agent(agent_name)
            agent_balance = simulate_one_episode(env, agent, num_steps=steps_per_simulation)
            all_scores[agent_name] += [agent_balance]

    print(f"Avg final scores of {num_simulations} simulations of {steps_per_simulation} steps:")
    for agent_name, final_balances in all_scores.items():
        print(f"\t-{agent_name}: {np.mean(final_balances)}")


def compare_single_episode():
    """
    Creates a progress log a single simulation for each agent and compare them

    TODO when there is learning the Logger is better to be moved to the episode level
    """
    for agent_type in ["Naive", "Greedy"]:
        env, agent = get_environment_and_agent(agent_type)
        simulation_logger = get_logger(log_dir=os.path.join(consts.SIMULATION_LOG_DIR, agent_type + '-logs'))
        simulate_one_episode(env, agent,
                             num_steps=consts.SIMULATION_STEPS,
                             simulation_logger=simulation_logger,
                             out_dir=consts.SIMULATION_OUT_DIR)

    compare_simulation_logs(consts.SIMULATION_LOG_DIR)


if __name__ == '__main__':
    compare_single_episode()
    # evaluate_agents(3, consts.SIMULATION_STEPS)
