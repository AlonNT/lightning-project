import os
from utils.graph_helpers import create_sub_graph_by_node_capacity
from Agents.random_agent import RandomInvestor
from Agents.greedy_agent import GreedyNodeInvestor
from Enviroments.lightning_enviroment import LightningEniroment
import opt

def get_environment_and_agent():
    graph = create_sub_graph_by_node_capacity(k=opt.ENVIROMENT_NUM_NODES, highest_capacity_offset=opt.ENIROMENT_DENSITY)
    env = LightningEniroment(graph)
    agent_pub_key = env.create_agent_node()
    if opt.AGENT_NAME == "Naive":
        agent = RandomInvestor(agent_pub_key, max_edges=opt.AGENT_MAX_EDGES)
    elif opt.AGENT_NAME == "Greedy":
        agent = GreedyNodeInvestor(agent_pub_key, max_edges=opt.AGENT_MAX_EDGES)
    else:
        raise Exception("No such agent")
    return env, agent


def get_agent_balance(env, agent):
    return agent.balance + env.get_node_balance(agent.pub_key)


def simulate(env, agent, num_steps=opt.SIMULATION_STEPS):
    os.makedirs(opt.SIMULATION_OUT_DIR, exist_ok=True)
    print("Simulating investment")
    state = env.get_state()
    for step in range(num_steps):
        env.render(save_path=os.path.join(opt.SIMULATION_OUT_DIR, f"step-%d"%step))
        print("Step %d:" % step)
        agent_balance = get_agent_balance(env, agent)
        print("\tAgent | balance: %d" % agent_balance)

        action = agent.act(state)
        new_state = env.step(action)
        state = new_state


def main():
    env, agent = get_environment_and_agent()
    simulate(env, agent)

if __name__ == '__main__':
    main()
