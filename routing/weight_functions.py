from typing import Callable

LND_DEFAULT_RISK_FACTOR = 15. / 10**9


def get_weight_function(implementation: str) -> Callable:
    if implementation.lower() == 'lnd':
        return lnd_weight
    else:
        raise ValueError(f'Implementation \'{implementation}\' is not supported.')


def lnd_weight(amount: int, base_fee: float, proportional_fee: float, delay: int,
               risk_factor: float = LND_DEFAULT_RISK_FACTOR) -> float:
    fee: float = base_fee + amount * proportional_fee
    weight: float = fee + amount * delay * risk_factor

    return weight
