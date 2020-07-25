# Control the experiments with this constants

ENVIROMENT_NUM_NODES = 100
ENIROMENT_DENSITY = 50 #  The bigger this is the sparse the network goes
ENVIROMENT_TRANSFERS_PER_STEP = 20
ENVIROMENT_TRANSFERS_MAX_AMOUNT = 10000
SIMULATION_STEPS = 500
SIMULATION_LOG_FREQ=10
SIMULATION_OUT_DIR = None # None to avoid visualization dumping
SIMULATION_LOG_DIR = "TRAIN_DIR" # None to avoid logging
AGENT_MAX_EDGES = 10
LN_DEFAULT_CHANNEL_COST = 0
# AGENT_NAME = "Naive"
# AGENT_NAME = "Greedy"
AGENT_NAME = "Kmeans"

# TODO: Find the default values
LND_DEFAULT_POLICY = {"time_lock_delta": 144, "fee_base_msat": 1000, "fee_rate_milli_msat": 0.001}
