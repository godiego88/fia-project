"""
Market Price Ingestion

Loads full price series.
Never silently drops assets.
Accepts structured universe entries or raw tickers.
"""

from typing import Dict, List, Union
import logging
import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def _extract_ticker(asset: Union[str, dict]) -> str:
    if isinstance(asset, str):
        return asset.strip().upper()

    if isinstance(asset, dict) and "ticker" in asset:
        return str(asset["ticker"]).strip().upper()

    raise RuntimeError(f"Invalid universe entry: {asset}")


def load_market_prices(universe: List[Union[str, dict]]) -> Dict[str, dict]:
    if not universe:
        raise RuntimeError("Market ingestion received empty universe")

    results: Dict[str, dict] = {}

    for asset in universe:
        ticker = _extract_ticker(asset)

        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                progress=False,
                auto_adjust=True,
            )

            if data.empty or "Close" not in data:
                results[ticker] = {
                    "status": "failed",
                    "reason": "no_price_data",
                    "price_series": None,
                }
                continue

            close = data["Close"].dropna()

            results[ticker] = {
                "status": "ok",
                "reason": None,
                "price_series": close.tolist(),
                "latest_price": float(close.iloc[-1]),
                "volatility": float(close.pct_change().std()),
            }

        except Exception as e:
            results[ticker] = {
                "status": "failed",
                "reason": str(e),
                "price_series": None,
            }

    if not results:
        raise RuntimeError("Market ingestion produced no results")

    return results
