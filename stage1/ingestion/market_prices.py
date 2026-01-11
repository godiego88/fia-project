"""
Market Price Ingestion — Explicit failure accounting
"""

from typing import Dict, List
import yfinance as yf


def load_market_prices(universe: List[str]) -> Dict[str, dict]:
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
                results[ticker] = {
                    "latest_price": None,
                    "status": "failed",
                    "reason": "no_data",
                }
                continue

            results[ticker] = {
                "latest_price": float(data["Close"].iloc[-1]),
                "status": "ok",
                "reason": None,
            }

        except Exception as e:
            results[ticker] = {
                "latest_price": None,
                "status": "failed",
                "reason": str(e),
            }

    return results
