import networkx as nx
from matplotlib import pyplot as plt
from LightningGraph.helpers import create_sub_graph_by_highest_node_capacity
from Agents.random_agent import RandomInvestor
from Enviroments.manager import Manager


def get_environment_and_agent():
    graph = create_sub_graph_by_highest_node_capacity(k=50)
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
        action = agent.act(state)
        new_state = env.step(action)
        agent_balance = get_agent_balance(env, agent)
        print("Step %d:" % step)
        print("# Agent balance: %d" % agent_balance)

        state = new_state


def main():
    env, agent = get_environment_and_agent()
    simulate(env, agent)

    plt.figure()
    nx.draw(env.get_state(), with_labels=True, font_weight='bold')
    plt.show(block=False)
    plt.savefig("Graph.png")


if __name__ == '__main__':
    main()
