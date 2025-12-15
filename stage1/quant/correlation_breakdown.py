"""
Correlation Breakdown Quant Module

Detects structural correlation changes via rolling
off-diagonal correlation deltas.

Canon reference:
- Correlation breakdown via rolling off-diagonal deltas
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import Dict, List
import statistics


def _returns(series: List[float]) -> List[float]:
    return [
        (series[i] - series[i - 1]) / series[i - 1]
        for i in range(1, len(series))
        if series[i - 1] != 0
    ]


def _correlation(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Invalid series length")

    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = sum((a - mean_x) ** 2 for a in x)
    den_y = sum((b - mean_y) ** 2 for b in y)

    if den_x == 0 or den_y == 0:
        raise ValueError("Zero variance")

    return num / (den_x * den_y) ** 0.5


def correlation_breakdown_signal(
    price_series: Dict[str, List[float]],
    window: int,
) -> float:
    """
    Compute correlation breakdown signal.

    Args:
        price_series: Mapping asset -> ordered price series
        window: Rolling window length for correlation

    Returns:
        Normalized correlation breakdown signal ∈ [0,1]
    """
    if len(price_series) < 2:
        return 0.0

    returns = {}
    for asset, prices in price_series.items():
        r = _returns(prices)
        if len(r) >= window * 2:
            returns[asset] = r

    assets = list(returns.keys())
    if len(assets) < 2:
        return 0.0

    deltas = []

    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            a, b = assets[i], assets[j]
            r1, r2 = returns[a], returns[b]

            try:
                corr_prev = _correlation(
                    r1[-2 * window:-window],
                    r2[-2 * window:-window],
                )
                corr_curr = _correlation(
                    r1[-window:],
                    r2[-window:],
                )
                deltas.append(abs(corr_curr - corr_prev))
            except ValueError:
                continue

    if not deltas:
        return 0.0

    # Normalize into [0,1]
    value = sum(deltas) / len(deltas)
    return min(max(value, 0.0), 1.0)
