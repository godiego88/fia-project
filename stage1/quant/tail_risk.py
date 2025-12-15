"""
Tail Risk Quant Module

Computes tail risk via Expected Shortfall (5%)
using a deterministic historical simulation approach.

Canon reference:
- Monte Carlo tail risk via Expected Shortfall (5%)
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List
import math


def _log_returns(prices: List[float]) -> List[float]:
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] <= 0 or prices[i] <= 0:
            continue
        returns.append(math.log(prices[i] / prices[i - 1]))
    return returns


def tail_risk_signal(
    price_series: List[float],
    alpha: float = 0.05,
) -> float:
    """
    Compute tail risk signal via Expected Shortfall.

    Args:
        price_series: Ordered price series
        alpha: Tail probability (default 5%)

    Returns:
        Normalized tail risk signal ∈ [0,1]
    """
    returns = _log_returns(price_series)
    if len(returns) < 10:
        return 0.0

    sorted_returns = sorted(returns)
    cutoff_index = int(len(sorted_returns) * alpha)

    if cutoff_index == 0:
        return 0.0

    tail_losses = sorted_returns[:cutoff_index]

    # Expected Shortfall is the mean of the worst alpha returns
    es = abs(sum(tail_losses) / len(tail_losses))

    # Normalize into [0,1] (canonical clamp)
    return min(max(es, 0.0), 1.0)
