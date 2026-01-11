"""
Stage 1 Runner

Signal-compression engine producing high-entropy triggers.
Authoritative orchestration layer. No simplification allowed.
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
    LOGGER.info("Stage 1 run started")

    universe = load_universe_from_google_sheets()
    if not universe:
        raise RuntimeError("Universe resolution returned empty list")

    market_data = load_market_prices(universe)

    quant_results = run_quant_analysis(
        market_data=market_data
    )

    nlp_results = run_nlp_analysis(
        universe=universe
    )

    nti = compute_nti(
        quant_results=quant_results,
        nlp_results=nlp_results,
        market_data=market_data,
    )

    trigger_context = {
        "timestamp": datetime.utcnow().isoformat(),
        "nti": nti,
        "trigger": nti["trigger"],
    }

    with open("trigger_context.json", "w") as f:
        json.dump(trigger_context, f, indent=2)

    with open("stage1_debug.json", "w") as f:
        json.dump(
            {
                "universe": universe,
                "market_data": market_data,
                "quant_results": quant_results,
                "nlp_results": nlp_results,
                "nti": nti,
            },
            f,
            indent=2,
        )

    LOGGER.info("Stage 1 completed successfully")


if __name__ == "__main__":
    main()
