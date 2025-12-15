"""
Volatility Regime Shift Quant Module

Detects volatility regime changes via divergence between
realized volatility and EMA-smoothed volatility.

Canon reference:
- Volatility regime shift via realized vs EMA divergence
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List
import math
import statistics


def _log_returns(prices: List[float]) -> List[float]:
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] <= 0 or prices[i] <= 0:
            continue
        returns.append(math.log(prices[i] / prices[i - 1]))
    return returns


def _ema(values: List[float], alpha: float) -> float:
    ema = values[0]
    for v in values[1:]:
        ema = alpha * v + (1 - alpha) * ema
    return ema


def volatility_regime_signal(
    price_series: List[float],
    realized_window: int,
    ema_window: int,
) -> float:
    """
    Compute volatility regime shift signal.

    Args:
        price_series: Ordered price series
        realized_window: Window for realized volatility
        ema_window: Window for EMA volatility smoothing

    Returns:
        Normalized volatility regime signal ∈ [0,1]
    """
    if len(price_series) <= max(realized_window, ema_window) + 1:
        return 0.0

    returns = _log_returns(price_series)
    if len(returns) <= realized_window:
        return 0.0

    realized_vols = []
    for i in range(realized_window, len(returns)):
        window = returns[i - realized_window:i]
        try:
            realized_vols.append(statistics.pstdev(window))
        except statistics.StatisticsError:
            continue

    if len(realized_vols) < ema_window:
        return 0.0

    alpha = 2 / (ema_window + 1)
    ema_vol = _ema(realized_vols[-ema_window:], alpha)
    current_vol = realized_vols[-1]

    if ema_vol <= 0:
        return 0.0

    divergence = abs(current_vol - ema_vol) / ema_vol

    # Canon normalization: clamp to [0,1]
    return min(max(divergence, 0.0), 1.0)
