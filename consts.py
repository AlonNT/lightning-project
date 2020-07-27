# Control the experiments with this constants

ENVIROMENT_NUM_NODES = 20
ENIROMENT_DENSITY = 100 #  The bigger this is the sparse the network goes
ENVIROMENT_TRANSFERS_PER_STEP = 1
ENVIROMENT_TRANSFERS_MAX_AMOUNT = 10000
SIMULATION_STEPS = 100
SIMULATION_LOG_FREQ=1
SIMULATION_OUT_DIR = "TRAIN_DIR" # None to avoid visualization dumping
SIMULATION_LOG_DIR = "TRAIN_DIR" # None to avoid logging
AGENT_MAX_EDGES = 10
LN_DEFAULT_CHANNEL_COST = 0 # TODO: Split agent score to locked money and channel opening cost

# TODO: Find the default values
LND_DEFAULT_POLICY = {"time_lock_delta": 144, "fee_base_msat": 1000, "fee_rate_milli_msat": 0.001}
