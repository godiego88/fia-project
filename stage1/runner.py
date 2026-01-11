"""
Stage 1 Runner – Signal Compression Engine

Produces high-entropy, sparse, regime-aware triggers.
"""

import json
import logging
from datetime import datetime

from stage1.ingestion.universe_loader import load_universe_from_google_sheets
from stage1.ingestion.market_prices import load_market_prices
from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("stage1-runner")


def main() -> None:
    universe = load_universe_from_google_sheets()
    market = load_market_prices(universe)

    prices = {
        k: v["latest_price"]
        for k, v in market.items()
        if v["status"] == "ok"
    }

    quant = run_quant_analysis(prices)
    nlp = run_nlp_analysis(universe)

    nti = compute_nti(quant, nlp)

    with open("trigger_context.json", "w") as f:
        json.dump(
            {"timestamp": datetime.utcnow().isoformat(), **nti},
            f,
            indent=2,
        )

    with open("stage1_debug.json", "w") as f:
        json.dump(
            {
                "universe": universe,
                "market": market,
                "quant": quant,
                "nlp": nlp,
                "nti": nti,
            },
            f,
            indent=2,
        )

    LOGGER.info("Stage 1 completed")


if __name__ == "__main__":
    main()
