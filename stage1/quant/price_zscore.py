"""
Price Z-Score Quant Module

Computes multi-horizon price Z-scores and normalizes them
according to the FIA Quant & Classical NLP Math Canon.

Canon reference:
- Multi-horizon price Z-scores normalized by |z| / 4
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List
import statistics


def _zscore(series: List[float]) -> float:
    """
    Compute the Z-score of the most recent value in a series.

    Returns:
        Z-score (can be negative or positive)
    """
    if len(series) < 2:
        raise ValueError("Insufficient data for z-score")

    mean = statistics.mean(series[:-1])
    stdev = statistics.pstdev(series[:-1])

    if stdev == 0:
        raise ValueError("Zero variance in series")

    return (series[-1] - mean) / stdev


def _normalize_z(z: float) -> float:
    """
    Normalize Z-score per canon: |z| / 4, clamped to [0,1].
    """
    value = abs(z) / 4.0
    return min(max(value, 0.0), 1.0)


def price_zscore_signal(
    price_series: List[float],
    horizons: List[int],
) -> float:
    """
    Compute the mean normalized Z-score across multiple horizons.

    Args:
        price_series: Full ordered price series (oldest → newest)
        horizons: List of lookback window sizes

    Returns:
        Normalized price signal ∈ [0,1]

    Notes:
        - Horizons with insufficient data are skipped
        - If all horizons are invalid, returns 0.0
    """
    scores = []

    for h in horizons:
        if len(price_series) <= h:
            continue

        window = price_series[-(h + 1):]

        try:
            z = _zscore(window)
            scores.append(_normalize_z(z))
        except ValueError:
            continue

    if not scores:
        return 0.0

    return sum(scores) / len(scores)
