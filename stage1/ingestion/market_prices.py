import yfinance as yf
import pandas as pd
from typing import List, Dict

from utils.logging import get_logger

LOGGER = get_logger("market-ingestion")


def load_market_prices(universe: List[str]) -> Dict[str, pd.Series]:
    if not universe:
        raise RuntimeError("Universe is empty — cannot load market prices")

    prices: Dict[str, pd.Series] = {}
    failed = []

    for ticker in universe:
        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                progress=False,
                auto_adjust=True,
                threads=False,
            )

            if data is None or data.empty:
                failed.append(ticker)
                LOGGER.warning(
                    "No market data returned",
                    extra={"ticker": ticker},
                )
                continue

            if "Close" not in data.columns:
                failed.append(ticker)
                LOGGER.warning(
                    "Missing Close column in market data",
                    extra={"ticker": ticker},
                )
                continue

            prices[ticker] = data["Close"]

            LOGGER.info(
                "Market data loaded",
                extra={
                    "ticker": ticker,
                    "points": len(data),
                    "latest_price": float(data["Close"].iloc[-1]),
                },
            )

        except Exception as e:
            failed.append(ticker)
            LOGGER.error(
                "Market data ingestion failed",
                extra={"ticker": ticker, "error": str(e)},
            )

    if not prices:
        raise RuntimeError("Market ingestion returned no usable data")

    coverage = len(prices) / len(universe)

    LOGGER.info(
        "Market ingestion completed",
        extra={
            "requested": len(universe),
            "loaded": len(prices),
            "failed": len(failed),
            "coverage": round(coverage, 3),
        },
    )

    return prices
