# Control the experiments with these constants

ENVIRONMENT_NUM_NODES = 20
ENVIRONMENT_DENSITY = 100  # The bigger this is the sparse the network goes
ENVIRONMENT_TRANSFERS_PER_STEP = 1
ENVIRONMENT_TRANSFERS_MAX_AMOUNT = 10000

SIMULATION_STEPS = 100
SIMULATION_LOG_FREQ = 1
SIMULATION_OUT_DIR = "TRAIN_DIR"  # None to avoid visualization dumping
SIMULATION_LOG_DIR = "TRAIN_DIR"  # None to avoid logging
AGENT_MAX_FUNDS = 10 ** 10

# The channel creation cost (which is the cost payed for the bitcoin miners
# to include the channel's creation transaction in their block).
# This value changes constantly (due to the dynamics of the bitcoin transactions' fees
# that change according to the load on the blockchain).
# This approximate value was calculated using buybitcoinworldwide.com to get the cost
# of a transaction (in usd), then converting us dollars to satoshis (in 8.8.2020).
# LN_DEFAULT_CHANNEL_COST = 40000
LN_DEFAULT_CHANNEL_COST = 0

# TODO: Find the actual default values in real life
LND_DEFAULT_POLICY = {"time_lock_delta": 144, "fee_base_msat": 1000, "fee_rate_milli_msat": 0.001}
