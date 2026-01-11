"""
Stage 1 Runner — Institutional Signal Compression Engine
High-entropy, sparse trigger generator for Stage 2
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

    quant = run_quant_analysis(market)
    nlp = run_nlp_analysis(universe)

    nti = compute_nti(
        quant_results=quant,
        nlp_results=nlp,
    )

    with open("trigger_context.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "trigger": nti["trigger"],
                "confidence": nti["confidence"],
                "regime": nti["regime"],
                "entropy": nti["entropy"],
            },
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


if __name__ == "__main__":
    main()
