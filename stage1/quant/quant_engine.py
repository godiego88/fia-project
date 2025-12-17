"""
Quantitative Analysis Engine

Implements canonical Stage 1 quantitative metrics
as defined in the FIA Quant & Classical NLP Math Canon.
"""

from typing import Dict
import pandas as pd


def run_quant_analysis(prices: Dict[str, pd.Series]) -> Dict[str, Dict[str, float]]:
    """
    Run quantitative analysis on market price series.

    Args:
        prices: Mapping of asset symbol -> price series (pd.Series)

    Returns:
        Dict mapping asset symbol -> quant metrics
    """
    results: Dict[str, Dict[str, float]] = {}

    for symbol, series in prices.items():
        if series is None or series.empty or len(series) < 2:
            continue

        # Ensure numeric, drop missing
        clean = pd.to_numeric(series, errors="coerce").dropna()
        if len(clean) < 2:
            continue

        returns = clean.pct_change().dropna()
        if returns.empty:
            continue

        # -----
        # CRITICAL FIX:
        # Explicit scalar extraction using .iloc[0]
        # This prevents FutureWarning and future TypeError
        # -----
        volatility = float(returns.std().iloc[0])
        mean_return = float(returns.mean().iloc[0])

        results[symbol] = {
            "volatility": volatility,
            "mean_return": mean_return,
        }

    return results
