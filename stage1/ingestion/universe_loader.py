"""
Universe Loader – Stage 1

Authoritative universe resolver.
Deterministic. Auditable. Fails hard if invalid.
"""

from typing import List
import logging

LOGGER = logging.getLogger("universe-loader")


def load_universe_from_google_sheets() -> List[str]:
    """
    Resolve securities universe.

    TEMP: static placeholder.
    Interface is final.
    """

    universe = [
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "AMZN",
    ]

    if not universe:
        raise RuntimeError("Universe loader returned empty universe")

    LOGGER.info("Universe resolved", extra={"count": len(universe)})
    return universe
