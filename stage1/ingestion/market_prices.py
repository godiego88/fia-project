"""
Stage 1 Market Price Ingestion

Fetches raw market price time series for configured assets.
This module performs NO analysis, NO scoring, and NO aggregation.

Responsibilities:
- Enforce quota limits via quota_manager
- Fetch price data
- Return normalized, deterministic structures
"""

import requests
from typing import Dict, List

from governance.quota_manager import is_allowed
from utils.io import load_yaml_config


def fetch_market_prices() -> Dict[str, List[float]]:
    """
    Fetch market prices for all configured assets.

    Returns:
        Dict[str, List[float]]:
            Mapping of asset symbol -> ordered price series
            Assets with missing or invalid data are excluded.
    """

    if not is_allowed("market_price_api"):
        # Silent degradation: skip ingestion entirely
        return {}

    assets_config = load_yaml_config("config/assets.yaml")
    api_config = assets_config.get("market_price_api", {})
    assets = assets_config.get("assets", [])

    base_url = api_config.get("base_url")
    price_field = api_config.get("price_field", "prices")

    if not base_url or not assets:
        return {}

    prices: Dict[str, List[float]] = {}

    for asset in assets:
        symbol = asset.get("symbol")
        endpoint = asset.get("endpoint")

        if not symbol or not endpoint:
            continue

        url = f"{base_url}/{endpoint}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception:
            # Degrade silently on API or parsing failure
            continue

        series = data.get(price_field)

        if not isinstance(series, list):
            continue

        # Ensure numeric-only, ordered series
        clean_series = []
        for value in series:
            try:
                clean_series.append(float(value))
            except (TypeError, ValueError):
                continue

        if clean_series:
            prices[symbol] = clean_series

    return prices
