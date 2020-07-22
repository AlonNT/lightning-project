from utils.graph_helpers import create_sub_graph_by_node_capacity
from Agents.random_agent import RandomInvestor
from Enviroments.manager import Manager
from utils.visualizers import visualize_balances
import os
import networkx as nx
MAX_TRIALS = 10000

def get_environment_and_agent():
    graph = create_sub_graph_by_node_capacity(k=10, highest_capacity_offset=50)
    env = Manager(graph)
    agent_pub_key = env.create_agent_node()
    agent = RandomInvestor(agent_pub_key)

    return env, agent


def get_agent_balance(env, agent):
    return agent.balance + env.get_node_balance(agent.pub_key)


def simulate(env, agent, num_steps=100):
    train_dir = "./Test_Training"
    os.makedirs(train_dir, exist_ok=True)
    print("Simulating investment")
    state, positions = env.get_state()
    for step in range(num_steps):

        visualize_balances(state, positions, save_path=os.path.join(train_dir, f"step-%d"%step))

        action = agent.act(state)
        new_state, positions = env.step(action)
        agent_balance = get_agent_balance(env, agent)
        print("Step %d:" % step)
        print("# Agent balance: %d" % agent_balance)

        state = new_state


def main():
    env, agent = get_environment_and_agent()
    simulate(env, agent)

if __name__ == '__main__':
    main()
