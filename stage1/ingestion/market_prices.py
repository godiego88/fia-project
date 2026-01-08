import logging
import yfinance as yf

logger = logging.getLogger("market-ingestion")


def load_market_data(ticker: str) -> dict | None:
    try:
        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df.empty or "Close" not in df:
            logger.warning(f"No usable market data for {ticker}")
            return None

        close = df["Close"]

        latest_price = float(close.iloc[-1])

        return {
            "ticker": ticker,
            "latest_price": latest_price,
            "history_len": len(close),
        }

    except Exception as e:
        logger.warning(f"{ticker} market ingestion failed: {e}")
        return None
