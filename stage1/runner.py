"""
Stage 1 Runner

Authoritative execution entrypoint for FIA Stage 1.
Stage 1 is ALWAYS observable, deterministic, and auditable.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from utils.io import load_yaml_config
from utils.logging import get_logger
from utils.state import (
    load_persistence,
    save_persistence,
    should_reset_persistence,
    mark_qualifying_run,
    save_last_run_id,
)

from stage1.ingestion.universe_loader import load_universe_from_google_sheets
from stage1.ingestion.market_prices import load_market_prices
from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti


LOGGER = get_logger("stage1-runner")


def _fail(reason: str) -> None:
    LOGGER.error("Stage 1 validation failure", extra={"reason": reason})
    raise RuntimeError(reason)


def main() -> None:
    run_id = str(uuid.uuid4())
    now = datetime.utcnow()

    LOGGER.info("Stage 1 run started", extra={"run_id": run_id})
    save_last_run_id(run_id)

    # --- Load configs ---
    assets_cfg = load_yaml_config("config/assets.yaml")
    nti_cfg = load_yaml_config("config/nt_thresholds.yaml")

    # --- Resolve universe ---
    universe = load_universe_from_google_sheets(assets_cfg)
    if not universe:
        _fail("Resolved universe is empty")

    LOGGER.info(
        "Resolved securities universe",
        extra={"count": len(universe), "tickers": universe},
    )

    # --- Market ingestion ---
    prices = load_market_prices(universe)
    if not prices:
        _fail("Market ingestion returned no data")

    # --- Quant analysis ---
    quant_results = run_quant_analysis(prices)
    if not quant_results:
        _fail("Quant engine produced no results")

    # --- NLP analysis ---
    nlp_results = run_nlp_analysis({"universe": universe})
    if not nlp_results:
        _fail("NLP engine produced no results")

    # --- Persistence handling ---
    persistence = load_persistence()
    if should_reset_persistence(now):
        persistence = 0

    # --- NTI computation (LOCKED CONTRACT) ---
    nti_result = compute_nti(
        quant_results=quant_results,
        nlp_results=nlp_results,
        persistence_value=persistence,
        nti_cfg=nti_cfg,
    )

    nti_value = nti_result.get("nti")
    nti_components = nti_result.get("components")
    nti_qualifies = nti_result.get("qualifies")

    if nti_value is None or nti_components is None:
        _fail("NTI computation incomplete")

    # --- Update persistence ---
    if nti_qualifies:
        persistence += 1
        mark_qualifying_run(now)
    else:
        persistence = 0

    save_persistence(persistence)

    # --- Trigger decision ---
    trigger_fired = (
        nti_value >= nti_cfg["trigger_threshold"]
        and persistence >= nti_cfg["required_persistence"]
    )

    # --- Trigger context (ALWAYS WRITTEN) ---
    trigger_context = {
        "run_id": run_id,
        "timestamp_utc": now.isoformat(),
        "universe": universe,
        "quant_results": quant_results,
        "nlp_results": nlp_results,
        "nti": nti_value,
        "nti_components": nti_components,
        "persistence": persistence,
        "trigger_fired": trigger_fired,
        "trigger_reason": (
            "NTI and persistence thresholds met"
            if trigger_fired
            else "Thresholds not met"
        ),
    }

    Path("trigger_context.json").write_text(
        json.dumps(trigger_context, indent=2),
        encoding="utf-8",
    )

    # --- Debug artifact (schema + config visibility) ---
    Path("stage1_debug.json").write_text(
        json.dumps(
            {
                "assets_cfg": assets_cfg,
                "nti_cfg": nti_cfg,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    LOGGER.info(
        "Stage 1 completed",
        extra={
            "nti": nti_value,
            "persistence": persistence,
            "trigger_fired": trigger_fired,
        },
    )


if __name__ == "__main__":
    main()
