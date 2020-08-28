import argparse

# ============== Experiment Configuration ============== #
parser = argparse.ArgumentParser(description='Experiment Configuration.')

# TODO # bitcoint == 10**8 satoshies but it seems like the fees are working with msat sot is it bitcoin == 10*11 msat ?
parser.add_argument('--INITIAL_FUNDS', type=int, default=10 ** 8, help='The initial funds of the agents.')
parser.add_argument('--SIMULATOR_TRANSFERS_MAX_AMOUNT', type=int, default=10 ** 4,
                    help='The maximal amount that can be transferred between two nodes.')
parser.add_argument('--LN_DEFAULT_CHANNEL_COST', type=int, default=4 * 10 ** 2,
                    help="""# The channel creation cost (which is the cost payed for the bitcoin miners
                            # to include the channel's creation transaction in their block).
                            # This value changes constantly (due to the dynamics of the bitcoin transactions' fees
                            # that change according to the load on the blockchain).
                            # This approximate value was calculated using buybitcoinworldwide.com to get the cost
                            # of a transaction (in usd), then converting us dollars to satoshis (in 8.8.2020).
                            # Warning: Changing this to 0 leads to bugs as agent open lots of channells""")
parser.add_argument('--SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION', type=int, default=1.0,
                    help='defines the balance in the other side of new channels in proportion of the first side balance')
parser.add_argument('--SIMULATOR_NUM_TRANSACTIONS', type=int, default=1000000,
                    help='How many transaction the simulator will simulate.')
parser.add_argument('--NUMBER_REPEATED_SIMULATIONS', type=int, default=5,
                    help='How many times to repeat the experiment, in order to get the mean & std of the reward in '
                         'each step..')
parser.add_argument('--SIMULATOR_NUM_NODES', type=int, default=50,
                    help='The size of the sub-graph of the lightning network to simulate.')
parser.add_argument('--GRAPH_DENSITY_OFFSET', type=int, default=50,
                    help='The higher this number the more sparse the sub-graph is.'
                         'The nodes will be ordered by some metric and the M next nodes will be selected..')
parser.add_argument('--DEBUG_OUT_DIR', type=str, default="Experiments",
                    help='Where to save plots and images.')
parser.add_argument('--VISUALIZE_TRANSACTIONS', action='store_true',
                    help='Turn on to create debug images of the transactionsin the simulator; this is very slow so '
                         'make sure you work with short simulations.')

args = parser.parse_args()

# TODO use args in main
INITIAL_FUNDS = args.INITIAL_FUNDS

SIMULATOR_TRANSFERS_MAX_AMOUNT = args.SIMULATOR_TRANSFERS_MAX_AMOUNT

LN_DEFAULT_CHANNEL_COST = args.LN_DEFAULT_CHANNEL_COST

SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION = args.SIMULATOR_PASSIVE_SIDE_BALANCE_PROPORTION

SIMULATOR_NUM_TRANSACTIONS = args.SIMULATOR_NUM_TRANSACTIONS

NUMBER_REPEATED_SIMULATIONS = args.NUMBER_REPEATED_SIMULATIONS

SIMULATOR_NUM_NODES = args.SIMULATOR_NUM_NODES

GRAPH_DENSITY_OFFSET = args.GRAPH_DENSITY_OFFSET

DEBUG_OUT_DIR = args.DEBUG_OUT_DIR

VISUALIZE_TRANSACTIONS = args.VISUALIZE_TRANSACTIONS
