"""
Stage 1 Runner

Authoritative execution entrypoint for FIA Stage 1.
Implements ingestion → quant → NLP → synthesis → NTI evaluation.

Silence is the default outcome.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from utils.state import (
    load_persistence,
    save_persistence,
    should_reset_persistence,
    mark_qualifying_run,
    save_last_run_id,
)
from utils.io import load_yaml_config
from utils.logging import get_logger

from stage1.ingestion.market_prices import load_market_prices
from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti


LOGGER = get_logger("stage1-runner")


def main() -> None:
    """
    Execute Stage 1 exactly once.
    """

    run_id = str(uuid.uuid4())
    now = datetime.utcnow()

    LOGGER.info("Stage 1 run started", extra={"run_id": run_id})
    save_last_run_id(run_id)

    # -------------------------
    # Load configuration
    # -------------------------
    assets_cfg = load_yaml_config("config/assets.yaml")
    nti_cfg = load_yaml_config("config/nt_thresholds.yaml")

    # -------------------------
    # Ingestion
    # -------------------------
    prices = load_market_prices(assets_cfg)

    if not prices:
        LOGGER.warning("No market data available — silent exit")
        return

    # -------------------------
    # Quant analysis
    # -------------------------
    quant_results = run_quant_analysis(prices)

    # -------------------------
    # NLP analysis
    # -------------------------
    nlp_results = run_nlp_analysis(assets_cfg)

    # -------------------------
    # NTI computation
    # -------------------------
    nti_result = compute_nti(
        quant_results=quant_results,
        nlp_results=nlp_results,
        nti_cfg=nti_cfg,
    )

    nti_value = nti_result["nti"]
    nti_components = nti_result["components"]
    nti_qualifies = nti_result["qualifies"]

    LOGGER.info(
        "NTI computed",
        extra={
            "nti": nti_value,
            "qualifies": nti_qualifies,
            "components": nti_components,
        },
    )

    # -------------------------
    # Persistence logic (CANONICAL)
    # -------------------------
    persistence = load_persistence()

    # Enforce decay before using persistence
    if should_reset_persistence(now):
        LOGGER.info("Persistence decayed — resetting")
        persistence = 0

    if nti_qualifies:
        persistence += 1
        mark_qualifying_run(now)
    else:
        persistence = 0

    save_persistence(persistence)

    LOGGER.info(
        "Persistence updated",
        extra={"persistence": persistence},
    )

    # -------------------------
    # Trigger decision
    # -------------------------
    if (
        nti_value >= nti_cfg["trigger_threshold"]
        and persistence >= nti_cfg["required_persistence"]
    ):
        LOGGER.warning("Stage 2 trigger condition met")

        trigger_context = {
            "run_id": run_id,
            "timestamp_utc": now.isoformat(),
            "nti": nti_value,
            "persistence": persistence,
            "nti_components": nti_components,
            "quant_results": quant_results,
            "nlp_results": nlp_results,
        }

        output_path = Path("trigger_context.json")
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(trigger_context, f, indent=2)

        LOGGER.warning("Trigger context written")

    else:
        LOGGER.info("No trigger — silent exit")


if __name__ == "__main__":
    main()
