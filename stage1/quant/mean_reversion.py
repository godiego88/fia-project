"""
Mean Reversion Quant Module

Computes a mean reversion signal as the normalized
distance between the current price and its moving average.

Canon reference:
- Mean reversion signal
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List
import statistics


def mean_reversion_signal(
    price_series: List[float],
    window: int,
) -> float:
    """
    Compute mean reversion signal.

    Args:
        price_series: Ordered price series
        window: Lookback window for moving average

    Returns:
        Normalized mean reversion signal ∈ [0,1]
    """
    if len(price_series) <= window:
        return 0.0

    window_prices = price_series[-window:]
    try:
        mean_price = statistics.mean(window_prices)
    except statistics.StatisticsError:
        return 0.0

    current_price = price_series[-1]

    if mean_price == 0:
        return 0.0

    deviation = abs(current_price - mean_price) / mean_price

    # Normalize into [0,1]
    return min(max(deviation, 0.0), 1.0)
