"""
Quantitative Analysis Engine

Implements canonical Stage 1 quantitative metrics
as defined in the FIA Quant & Classical NLP Math Canon.
"""

from typing import Dict, Any
import pandas as pd


def _extract_price_series(obj: Any) -> pd.Series | None:
    """
    Normalize various ingestion outputs into a single price Series.

    Accepts:
    - pd.Series
    - pd.DataFrame (uses first numeric column)
    - list / tuple (converted to Series)

    Returns:
    - pd.Series or None if extraction fails
    """
    if obj is None:
        return None

    # Case 1: Already a Series
    if isinstance(obj, pd.Series):
        return obj

    # Case 2: DataFrame → take first numeric column
    if isinstance(obj, pd.DataFrame):
        numeric_cols = obj.select_dtypes(include="number")
        if numeric_cols.empty:
            return None
        return numeric_cols.iloc[:, 0]

    # Case 3: List / tuple
    if isinstance(obj, (list, tuple)):
        return pd.Series(obj)

    return None


def run_quant_analysis(prices: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Run quantitative analysis on normalized price series.

    Args:
        prices: Mapping of asset symbol -> price data
                (Series, DataFrame, or list-like)

    Returns:
        Dict mapping asset symbol -> quant metrics
    """
    results: Dict[str, Dict[str, float]] = {}

    for symbol, raw in prices.items():
        series = _extract_price_series(raw)
        if series is None:
            continue

        # Ensure numeric and clean
        clean = pd.to_numeric(series, errors="coerce").dropna()
        if len(clean) < 2:
            continue

        returns = clean.pct_change().dropna()
        if returns.empty:
            continue

        # Explicit scalar extraction (future-safe)
        volatility = float(returns.std())
        mean_return = float(returns.mean())

        results[symbol] = {
            "volatility": volatility,
            "mean_return": mean_return,
        }

    return results
