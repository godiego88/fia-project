"""
Stage 1 Runner

Coordinates ingestion, quant, NLP, synthesis (NTI),
and decides whether to trigger Stage 2.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from stage1.ingestion.market_prices import fetch_market_prices
from stage1.ingestion.securities import resolve_securities_universe
from stage1.quant.engine import run_quant_analysis
from stage1.nlp.engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti


# ------------------------
# Configuration (LOCKED)
# ------------------------

NTI_THRESHOLD = 0.35
QUANT_STRENGTH_THRESHOLD = 0.25
PERSISTENCE_THRESHOLD = 0.60
NOVELTY_THRESHOLD = 0.50


# ------------------------
# Logging
# ------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("stage1-runner")


# ------------------------
# Runner
# ------------------------

def main() -> None:
    logger.info("Stage 1 run started")

    debug: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "initialized",
    }

    # 1. Resolve universe
    universe = resolve_securities_universe()
    logger.info("Resolved securities universe")

    debug["universe_size"] = len(universe)

    # 2. Ingest prices
    prices = fetch_market_prices(universe)

    # 3. Quant analysis
    quant_results = run_quant_analysis(prices)

    debug["quant_assets"] = list(quant_results.keys())
    debug["quant_count"] = len(quant_results)

    if not quant_results:
        debug["status"] = "no_quant_data"
        _write_debug(debug)
        logger.info("No quant results — exiting cleanly")
        return

    # 4. NLP analysis
    nlp_results = run_nlp_analysis(universe)
    logger.info("NLP analysis completed")

    # 5. NTI synthesis (authoritative)
    nti = compute_nti(
        quant=quant_results,
        nlp=nlp_results,
    )

    debug["nti"] = nti

    # 6. Extract gates
    quant_strength = nti["components"]["quant_strength"]
    persistence = nti["components"]["persistence"]
    novelty = nti["components"]["novelty"]
    nti_score = nti["score"]

    debug["gates"] = {
        "nti": nti_score,
        "quant_strength": quant_strength,
        "persistence": persistence,
        "novelty": novelty,
    }

    # 7. Trigger decision (HARD GATE)
    should_trigger = (
        nti_score >= NTI_THRESHOLD
        and quant_strength >= QUANT_STRENGTH_THRESHOLD
        and persistence >= PERSISTENCE_THRESHOLD
        and novelty >= NOVELTY_THRESHOLD
    )

    debug["trigger_stage2"] = should_trigger

    _write_debug(debug)

    if not should_trigger:
        logger.info("Stage 2 NOT triggered")
        return

    # 8. Emit trigger context
    trigger_context = {
        "timestamp": debug["timestamp"],
        "nti": nti_score,
        "components": nti["components"],
        "universe": universe,
    }

    with open("trigger_context.json", "w") as f:
        json.dump(trigger_context, f, indent=2)

    logger.info("Stage 2 TRIGGERED")


# ------------------------
# Utilities
# ------------------------

def _write_debug(payload: Dict[str, Any]) -> None:
    with open("stage1_debug.json", "w") as f:
        json.dump(payload, f, indent=2)


# ------------------------
# Entrypoint
# ------------------------

if __name__ == "__main__":
    main()
