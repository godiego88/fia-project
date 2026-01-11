"""
Universe Loader — Authoritative Asset Source

Deterministic.
No silent drops.
"""

import os
import logging
from typing import List

LOGGER = logging.getLogger("universe-loader")


def load_universe_from_google_sheets() -> List[str]:
    sheet = os.getenv("UNIVERSE_TICKERS")
    if not sheet:
        raise RuntimeError("UNIVERSE_TICKERS env var missing")

    universe = [s.strip().upper() for s in sheet.split(",") if s.strip()]

    if not universe:
        raise RuntimeError("Universe resolved empty")

    LOGGER.info("Universe loaded", extra={"count": len(universe)})
    return universe
