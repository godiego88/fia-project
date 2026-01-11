"""
Market Price Ingestion – Stage 1

Institution-grade loader.
Never silently drops assets.
"""

from typing import Dict, List
import logging
import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def load_market_prices(universe: List[str]) -> Dict[str, dict]:
    results: Dict[str, dict] = {}

    for ticker in universe:
        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                auto_adjust=True,
                progress=False,
            )

            if data.empty or "Close" not in data:
                results[ticker] = {
                    "status": "failed",
                    "reason": "no_price_data",
                    "prices": None,
                }
                continue

            results[ticker] = {
                "status": "ok",
                "reason": None,
                "prices": data["Close"].tolist(),
            }

        except Exception as e:
            results[ticker] = {
                "status": "failed",
                "reason": str(e),
                "prices": None,
            }

    if not results:
        raise RuntimeError("Market ingestion produced zero assets")

    return results
