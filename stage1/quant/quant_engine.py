"""
Quantitative analysis engine for FIA Stage 1.
"""

from typing import Dict
import pandas as pd


def run_quant_analysis(prices: Dict[str, pd.DataFrame]) -> dict:
    """
    Run canonical quantitative signals over price data.
    """
    results = {}

    for symbol, df in prices.items():
        if df.empty:
            continue

        returns = df["Close"].pct_change().dropna()

        results[symbol] = {
            "volatility": float(returns.std()),
            "mean_return": float(returns.mean()),
        }

    return results
