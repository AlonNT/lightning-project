import os
import matplotlib.pyplot as plt
from time import time
import pickle
import numpy as np

class logger(object):
    """Basic logger of training progress"""
    def __init__(self, log_frequency, logdir='LOGS'):
        os.makedirs(logdir, exist_ok=True)
        self.logdir = logdir
        self.log_frequency = log_frequency
        self.score_per_step = []
        # self.completed_transfers_per_step = []
        self.train_start = time()
        self.total_steps = 0


    def log_step(self, agent_balance): #, completed_transfers):
        self.score_per_step += [agent_balance]
        # self.completed_transfers_per_step += [completed_transfers]
        self.total_steps += 1
        if self.total_steps % self.log_frequency == 0:
            self.output_stats()

    def output_stats(self):
        print('Steps done: ', self.total_steps)
        print(f"\t# Agent balance: {self.score_per_step[-1]}")
        time_passed = time() - self.train_start
        print("\t# steps/sec avg: %.3f " % (self.total_steps / time_passed))
        xs = np.arange(1, self.total_steps + 1)

        plt.plot(xs, self.score_per_step, label='Balance')
        plt.ylabel('Balance')
        plt.xlabel('Step')
        plt.legend()
        plt.savefig(os.path.join(self.logdir, "Agent-balance.png"))
        plt.clf()

        # plt.plot(xs, self.completed_transfers_per_step, label='Complete transfers')
        # plt.ylabel('Complete transfers')
        # plt.xlabel('Step')
        # plt.legend()
        # plt.savefig(os.path.join(self.logdir, "transfers.png"))
        # plt.clf()

    def pickle_episode_scores(self):
        f = open(os.path.join(self.logdir, "step_scores.pkl"), 'wb')
        pickle.dump(self.score_per_step, f)
