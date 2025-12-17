"""
Market price ingestion for FIA Stage 1.

Loads historical market price data for configured assets.
No placeholders. No synthetic data.
"""

from typing import Dict
import pandas as pd
import yfinance as yf


def load_market_prices(assets_cfg: dict) -> Dict[str, pd.DataFrame]:
    """
    Load historical market prices for all configured assets.

    Returns:
        Dict[symbol, DataFrame] with OHLCV data.
    """
    results: Dict[str, pd.DataFrame] = {}

    assets = assets_cfg.get("assets", [])
    if not assets:
        return results

    for asset in assets:
        symbol = asset.get("symbol")
        lookback_days = asset.get("lookback_days", 365)

        if not symbol:
            continue

        try:
            df = yf.download(
                tickers=symbol,
                period=f"{lookback_days}d",
                auto_adjust=True,
                progress=False,
            )

            if df is None or df.empty:
                continue

            results[symbol] = df

        except Exception:
            # Silence is correct — ingestion failure ≠ system failure
            continue

    return results
