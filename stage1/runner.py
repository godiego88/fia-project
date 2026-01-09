"""
Stage 1 Runner

Coordinates ingestion, quant scoring, NLP analysis, and NTI synthesis.
Emits trigger_context.json and stage1_debug.json for Stage 2.
"""

import json
import logging
from pathlib import Path

from stage1.ingestion.market_prices import load_market_prices
from stage1.synthesis.nti import compute_nti
from stage1.nlp.engine import run_nlp_analysis
from stage1.universe import resolve_securities_universe
from stage1.quant.engine import run_quant_analysis

LOGGER = logging.getLogger("stage1-runner")
logging.basicConfig(level=logging.INFO)


TRIGGER_CONTEXT_PATH = Path("trigger_context.json")
DEBUG_PATH = Path("stage1_debug.json")


def main() -> None:
    LOGGER.info("Stage 1 run started")

    # 1. Resolve universe
    universe = resolve_securities_universe()
    if not universe:
        raise RuntimeError("Resolved empty securities universe")

    LOGGER.info("Resolved securities universe")

    # 2. Market data ingestion (authoritative, non-dropping)
    market_data = load_market_prices(universe)

    # 3. Quant analysis (may return empty, must not crash Stage 1)
    quant_results = run_quant_analysis(
        universe=universe,
        market_data=market_data,
    )

    # 4. NLP analysis
    nlp_results = run_nlp_analysis(universe)
    LOGGER.info("NLP analysis completed")

    # 5. NTI synthesis (FINAL, LOCKED)
    nti_result = compute_nti(
        quant_results=quant_results,
        nlp_results=nlp_results,
        market_data=market_data,
    )

    # 6. Emit outputs for Stage 2
    trigger_context = {
        "nti": nti_result,
        "universe_size": len(universe),
    }

    debug_payload = {
        "universe": universe,
        "market_data": market_data,
        "quant_results": quant_results,
        "nlp_results": nlp_results,
        "nti": nti_result,
    }

    TRIGGER_CONTEXT_PATH.write_text(json.dumps(trigger_context, indent=2))
    DEBUG_PATH.write_text(json.dumps(debug_payload, indent=2))

    LOGGER.info("Stage 1 completed successfully")


if __name__ == "__main__":
    main()
