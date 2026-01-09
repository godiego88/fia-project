"""
Stage 1 Runner

Coordinates ingestion, quant, NLP, and NTI synthesis.
This file is authoritative and must match repo structure exactly.
"""

import json
import logging
from datetime import datetime

from stage1.ingestion.universe_loader import load_universe_from_google_sheets
from stage1.ingestion.market_prices import load_market_prices
from stage1.quant.engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("stage1-runner")


def main() -> None:
    LOGGER.info("Stage 1 run started")

    # 1. Resolve universe
    universe = load_universe_from_google_sheets()
    if not universe:
        raise RuntimeError("Universe resolution returned empty list")

    LOGGER.info("Resolved securities universe")

    # 2. Market ingestion
    market_data = load_market_prices(universe)

    # 3. Quant analysis (only assets with prices)
    price_series = {
        ticker: data["latest_price"]
        for ticker, data in market_data.items()
        if data["status"] == "ok"
    }

    quant_results = run_quant_analysis(price_series)

    # 4. NLP analysis
    nlp_results = run_nlp_analysis(universe)

    # 5. NTI synthesis (canonical)
    nti_result = compute_nti(
        quant_results=quant_results,
        nlp_results=nlp_results,
    )

    # 6. Emit artifacts
    trigger_context = {
        "timestamp": datetime.utcnow().isoformat(),
        "nti": nti_result,
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
                "nti": nti_result,
            },
            f,
            indent=2,
        )

    LOGGER.info("Stage 1 completed successfully")


if __name__ == "__main__":
    main()
