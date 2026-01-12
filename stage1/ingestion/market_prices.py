from typing import Dict, List
import logging
import yfinance as yf

LOGGER = logging.getLogger("market-ingestion")


def load_market_prices(universe: List[Dict[str, str]]) -> Dict[str, dict]:
    if not universe:
        raise RuntimeError("Market ingestion received empty universe")

    results: Dict[str, dict] = {}

    for asset in universe:
        if not isinstance(asset, dict) or "ticker" not in asset:
            raise RuntimeError(f"Invalid universe entry: {asset}")

        ticker = asset["ticker"]

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
