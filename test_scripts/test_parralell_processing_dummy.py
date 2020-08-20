from copy import deepcopy
import numpy as np
from multiprocessing import Pool
from time import time
import random

REPS=1
NUM_WORKERS=1
RANDOM_MATRICES = [np.random.rand(100,10) for _ in range(10000)]
RANDOM_lists = [np.random.rand(100,10) for _ in range(10000)]


def dummy_work():



def work_parrallel():
    chunk_size = len(RANDOM_MATRICES) // NUM_WORKERS
    # chunks = [RANDOM_MATRICES[i:i + chunk_size] for i in range (0, len(RANDOM_MATRICES), chunk_size)]
    with Pool (NUM_WORKERS) as p:
        res = p.map (np.mean, RANDOM_MATRICES, chunk_size)
        return dict(zip(range(len(RANDOM_MATRICES)), res))

def work():
    results = dict()
    for i, mat in enumerate(RANDOM_MATRICES):
        results[i] = mat.mean()
    return results

if __name__ == '__main__':
    start = time()
    for rep in range(REPS):
        res_sync = work()
    print(f"sync takes: {(time()-start)/REPS}")

    start = time()
    for rep in range (REPS):
        res_async = work_parrallel()
    print(f"Async takes: {(time()-start)/REPS}")

    print(len(res_sync), len(res_async))
