import os
from utils.graph_helpers import create_sub_graph_by_node_capacity
from Agents.random_agent import RandomInvestor
from Agents.greedy_agent import GreedyNodeInvestor
from Agents.Kmeans_agent import KmeansInvestor
from Enviroments.lightning_enviroment import LightningEniroment
from utils.visualizers import create_simulation_gif, compare_simulation_logs
from utils.loggers import logger
import numpy as np
import consts


def get_environment_and_agent(agent_name):
    graph = create_sub_graph_by_node_capacity(k=consts.ENVIROMENT_NUM_NODES,
                                              highest_capacity_offset=consts.ENIROMENT_DENSITY)
    env = LightningEniroment(graph, tranfers_per_step=consts.ENVIROMENT_TRANSFERS_PER_STEP,
                             transfer_max_amount=consts.ENVIROMENT_TRANSFERS_MAX_AMOUNT)
    agent_pub_key = env.create_agent_node()
    if agent_name == "Naive":
        agent = RandomInvestor(agent_pub_key, max_edges=consts.AGENT_MAX_EDGES)
    elif agent_name == "Greedy":
        agent = GreedyNodeInvestor(agent_pub_key, max_edges=consts.AGENT_MAX_EDGES)
    elif agent_name == "Kmeans":
        agent = KmeansInvestor(agent_pub_key, max_edges=consts.AGENT_MAX_EDGES)
    else:
        raise Exception("No such agent")
    return env, agent


def get_agent_balance(env, agent):
    # TODO change name from balance to reward
    return agent.balance + env.get_node_balance(agent.pub_key)


def get_logger(logg_dir):
    if consts.SIMULATION_LOG_DIR is not None:
        simulation_logger = logger(consts.SIMULATION_LOG_FREQ, logg_dir)
    else:
        simulation_logger = None
    return simulation_logger


def simulate_one_episode(env, agent, num_steps, simulation_logger=None, out_dir=None):
    print("Simulating investment")
    state = env.get_state()
    for step in range(num_steps):
        agent_balance = get_agent_balance(env, agent)
        if simulation_logger is not None:
            simulation_logger.log_step(agent_balance)
        if out_dir is not None:
            env.render(save_path=os.path.join(out_dir, "frames", f"step-%s" % str(step).zfill(3)),
                       agent_balance=agent_balance)

        action = agent.act(state)
        new_state = env.step(action)
        state = new_state

    # Finalize
    if out_dir is not None:
        create_simulation_gif(os.path.join(out_dir, "frames"))
    if simulation_logger is not None:
        simulation_logger.pickle_episode_scores()

    return agent_balance  # return final balance: the episode score


def evaluate_agents(num_simmulations, steps_per_simulation):
    """Average simulations final balances for all each agents and compare them"""
    agents_names = ["Naive", "Greedy", "Kmeans"]
    all_scores = {name:[] for name in agents_names}
    for agent_name in agents_names:
        for e in range(num_simmulations):
            env, agent = get_environment_and_agent(agent_name)
            agent_balance = simulate_one_episode(env, agent, num_steps=steps_per_simulation,
                                                             simulation_logger=None,
                                                             out_dir=None)
            all_scores[agent_name] += [agent_balance]

    print(f"Avg final scores of {num_simmulations} simulations of {steps_per_simulation} steps")
    for agent_name, final_balances in all_scores.items():
        print(f"\t-{agent_name}: {np.mean(final_balances)}")


def compare_single_episode():
    """Creates a progress log a single simulaion for each agent and compare them
    # TODO: when there is learning the logger is better to be moved to the episode level
    """
    for agent_name in ["Naive", "Greedy", "Kmeans"]:
        env, agent = get_environment_and_agent(agent_name)
        simulation_logger = get_logger(os.path.join(consts.SIMULATION_LOG_DIR, agent_name + '-loggs'))
        simulate_one_episode(env, agent, num_steps=consts.SIMULATION_STEPS,
                             simulation_logger=simulation_logger,
                             out_dir=consts.SIMULATION_OUT_DIR)

    compare_simulation_logs(consts.SIMULATION_LOG_DIR)


if __name__ == '__main__':
    compare_single_episode()
    # evaluate_agents(3, consts.SIMULATION_STEPS)


