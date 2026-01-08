from typing import List, Dict
import pandas as pd
import yfinance as yf

from utils.logging import get_logger

LOGGER = get_logger("market-ingestion")


def load_market_prices(universe: List[str]) -> Dict[str, pd.Series]:
    if not universe:
        raise RuntimeError("Universe is empty — cannot load market prices")

    prices: Dict[str, pd.Series] = {}
    failures = {}

    for ticker in universe:
        try:
            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if data is None or data.empty or "Close" not in data.columns:
                failures[ticker] = "no_close_data"
                LOGGER.warning("No usable market data", extra={"ticker": ticker})
                continue

            close = data["Close"].astype(float)
            prices[ticker] = close

            LOGGER.info(
                "Market data loaded",
                extra={
                    "ticker": ticker,
                    "points": len(close),
                    "latest_price": float(close.iloc[-1]),
                },
            )

        except Exception as e:
            failures[ticker] = str(e)
            LOGGER.error(
                "Market ingestion failed",
                extra={"ticker": ticker, "error": str(e)},
            )

    if not prices:
        raise RuntimeError("Market ingestion returned zero valid tickers")

    LOGGER.info(
        "Market ingestion completed",
        extra={
            "requested": len(universe),
            "loaded": len(prices),
            "failed": len(failures),
        },
    )

    return prices
