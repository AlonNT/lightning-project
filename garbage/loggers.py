import os
import matplotlib.pyplot as plt
from time import time
import pickle
import numpy as np
from typing import List


class Logger(object):
    """
    Basic Logger of the simulation progress
    """

    def __init__(self, log_frequency: int, logdir: str = 'LOGS'):
        self.logdir: str = logdir                  # The directory where the logs will be created.
        self.score_per_step: List[int] = list()    # The scores the agent made in each step of the simulation.
        self.start_time: float = time()            # The starting time of the simulation.
        self.total_steps: int = 0                  # The total number of steps of the simulation.
        # self.completed_transfers_per_step = []

        os.makedirs(logdir, exist_ok=True)

    def log_step(self, agent_reward):  # , completed_transfers):
        """
        Log a single step of the simulation.
        It updates the relevant variables, and output statistics every 'self.log_frequency' iterations.
        :param agent_reward: The current agent's reward.
        """
        self.score_per_step.append(agent_reward)
        # self.completed_transfers_per_step += [completed_transfers]
        self.total_steps += 1
        if self.total_steps % self.log_frequency == 0:
            self.output_stats()

    def output_stats(self):
        """
        Output statistics for the current step in the simulation.
        This includes printing the average reward and steps per second,
        as well as a plot of the rewards in each step of the simulation so far.
        """
        print('Steps done: ', self.total_steps)
        print(f"\t# Agent's reward': {self.score_per_step[-1]}")
        time_passed = time() - self.start_time
        print("\t# steps/sec avg: %.3f " % (self.total_steps / time_passed))
        xs = np.arange(1, self.total_steps + 1)

        plt.plot(xs, self.score_per_step, label='Reward')
        plt.ylabel('Reward')
        plt.xlabel('Step')
        plt.legend()
        plt.savefig(os.path.join(self.logdir, "Agent-reward.png"))
        plt.clf()

        # plt.plot(xs, self.completed_transfers_per_step, label='Complete transfers')
        # plt.ylabel('Complete transfers')
        # plt.xlabel('Step')
        # plt.legend()
        # plt.savefig(os.path.join(self.logdir, "transfers.png"))
        # plt.clf()

    # TODO delete
    def pickle_episode_scores(self):
        """
        Dumps the scores per step in a pickle file inside the lig directory.
        """
        with open(os.path.join(self.logdir, "score_per_step.pkl"), 'wb') as f:
            pickle.dump(self.score_per_step, f)
