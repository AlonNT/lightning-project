#### LND ####
RiskFactorBillionths = 15. / 1000000000
# This is the implementation of the method `FindRoutes` in lnd.routing.router.go (a modification to Yen's algorithm)
# and `routing.pathfind.findPath`, line 635, 640
def lnd_weight(channel, amount, prev_weight, *args, **kwargs):
    fee = channel.base_fee + (amount * channel.proportional_fee)
    time_lock_penalty = prev_weight + amount * channel.delay * RiskFactorBillionths + fee
    return amount + fee, time_lock_penalty
