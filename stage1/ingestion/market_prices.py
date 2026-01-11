from typing import Dict, List
import logging
import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def load_market_prices(universe: List[str]) -> Dict[str, dict]:
    if not universe:
        raise RuntimeError("Market ingestion received empty universe")

    results = {}

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
                    "reason": "no_price_data",
                }
                continue

            latest_price = float(data["Close"].iloc[-1])

            results[ticker] = {
                "latest_price": latest_price,
                "status": "ok",
                "reason": None,
            }

        except Exception as e:
            results[ticker] = {
                "latest_price": None,
                "status": "failed",
                "reason": str(e),
            }

    if not results:
        raise RuntimeError("Market ingestion produced no results")

    return results
