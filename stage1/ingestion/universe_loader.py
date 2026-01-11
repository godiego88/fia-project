"""
Universe Loader

Authoritative universe source.
Must never silently return empty.
"""

from typing import List
import os
import logging

LOGGER = logging.getLogger("universe-loader")


def load_universe_from_google_sheets() -> List[str]:
    # Placeholder for authoritative loader
    universe = os.getenv("STATIC_UNIVERSE", "").split(",")

    universe = [u.strip().upper() for u in universe if u.strip()]

    if not universe:
        raise RuntimeError("Universe loader produced empty universe")

    LOGGER.info("Universe loaded", extra={"count": len(universe)})
    return universe
