"""
Market Price Ingestion

Authoritative market data loader for Stage 1.
Must NEVER silently drop assets.
"""

from typing import Dict, List
import logging

import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def load_market_prices(universe: List[str]) -> Dict[str, dict]:
    """
    Load recent market prices for a universe of tickers.

    Returns:
      dict[ticker] -> {
        "latest_price": float | None,
        "status": "ok" | "failed",
        "reason": str | None
      }
    """

    if not universe:
        raise RuntimeError("Market ingestion received empty universe")

    results: Dict[str, dict] = {}

    for ticker in universe:
        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                progress=False,
                auto_adjust=True,
            )

            if data.empty or "Close" not in data:
                LOGGER.warning("No usable market data", extra={"ticker": ticker})
                results[ticker] = {
                    "latest_price": None,
                    "status": "failed",
                    "reason": "no_price_data",
                }
                continue

            close = data["Close"]
            latest_price = float(close.iloc[-1])

            results[ticker] = {
                "latest_price": latest_price,
                "status": "ok",
                "reason": None,
            }

            LOGGER.info("Market data loaded", extra={"ticker": ticker})

        except Exception as e:
            LOGGER.exception("Market ingestion failed", extra={"ticker": ticker})
            results[ticker] = {
                "latest_price": None,
                "status": "failed",
                "reason": str(e),
            }

    if not results:
        raise RuntimeError("Market ingestion produced no results")

    LOGGER.info("Market ingestion completed", extra={"count": len(results)})
    return results
