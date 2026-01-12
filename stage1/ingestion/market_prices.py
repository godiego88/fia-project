"""
Market Price Ingestion

Loads full price series.
Never silently drops assets.
"""

from typing import Dict, List
import logging
import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def load_market_prices(universe: List[dict]) -> Dict[str, dict]:
    if not universe:
        raise RuntimeError("Market ingestion received empty universe")

    # ---- HARD SCHEMA VALIDATION ----
    tickers: List[str] = []
    for asset in universe:
        if "ticker" not in asset:
            raise RuntimeError(f"Invalid universe entry: {asset}")
        tickers.append(asset["ticker"])

    results: Dict[str, dict] = {}

    for ticker in tickers:
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
            LOGGER.exception("Market ingestion failed", extra={"ticker": ticker})
            results[ticker] = {
                "status": "failed",
                "reason": str(e),
                "price_series": None,
            }

    if not results:
        raise RuntimeError("Market ingestion produced no results")

    return results
