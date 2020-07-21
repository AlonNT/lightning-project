import networkx as nx
from utils.graph_helpers import create_sub_graph_by_node_capacity
from Agents.random_agent import RandomInvestor
from Enviroments.manager import Manager
from utils.visualizers import visualize_balances
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
    print("Simulating investment")
    state = env.get_state()
    for step in range(num_steps):
        visualize_balances(state)
        action = agent.act(state)
        new_state = env.step(action)
        agent_balance = get_agent_balance(env, agent)
        print("Step %d:" % step)
        print("# Agent balance: %d" % agent_balance)

        state = new_state


def main():
    env, agent = get_environment_and_agent()
    simulate(env, agent)

if __name__ == '__main__':
    main()
