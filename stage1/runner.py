"""
Stage 1 Runner

Authoritative execution entrypoint for FIA Stage 1.
Stage 1 is ALWAYS observable and deterministic.
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
from stage1.ingestion.universe_loader import load_universe_from_google_sheets
from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti


LOGGER = get_logger("stage1-runner")


def main() -> None:
    run_id = str(uuid.uuid4())
    now = datetime.utcnow()

    LOGGER.info("Stage 1 run started", extra={"run_id": run_id})
    save_last_run_id(run_id)

    trigger_context = {
        "run_id": run_id,
        "timestamp_utc": now.isoformat(),
        "universe": [],
        "quant_results": None,
        "nlp_results": None,
        "nti": None,
        "nti_components": None,
        "persistence": None,
        "trigger_fired": False,
        "trigger_reason": None,
        "errors": [],
    }

    try:
        assets_cfg = load_yaml_config("config/assets.yaml")
        nti_cfg = load_yaml_config("config/nt_thresholds.yaml")

        universe = load_universe_from_google_sheets(assets_cfg)
        if not universe:
            raise RuntimeError("Universe resolution returned empty list")

        trigger_context["universe"] = universe
        LOGGER.info(
            "Resolved securities universe",
            extra={"count": len(universe), "tickers": universe},
        )

        prices = load_market_prices(universe)
        if not prices:
            raise RuntimeError("Market ingestion returned no data")

        quant_results = run_quant_analysis(prices)
        if not quant_results:
            raise RuntimeError("Quant engine produced no results")

        trigger_context["quant_results"] = quant_results

        nlp_results = run_nlp_analysis({"universe": universe})
        if not nlp_results:
            raise RuntimeError("NLP engine produced no results")

        trigger_context["nlp_results"] = nlp_results

        persistence = load_persistence()
        if should_reset_persistence(now):
            persistence = 0

        nti_result = compute_nti(
            quant_results=quant_results,
            nlp_results=nlp_results,
            persistence_value=persistence,
            nti_cfg=nti_cfg,
        )

        trigger_context["nti"] = nti_result["nti"]
        trigger_context["nti_components"] = nti_result["components"]

        if nti_result["qualifies"]:
            persistence += 1
            mark_qualifying_run(now)
        else:
            persistence = 0

        save_persistence(persistence)
        trigger_context["persistence"] = persistence

        trigger_fired = (
            nti_result["nti"] >= nti_cfg["trigger"]["nti_min_value"]
            and persistence >= nti_cfg["trigger"]["required_consecutive_runs"]
        )

        trigger_context["trigger_fired"] = trigger_fired
        trigger_context["trigger_reason"] = (
            "NTI and persistence thresholds met"
            if trigger_fired
            else "Thresholds not met"
        )

        LOGGER.info(
            "Stage 1 completed",
            extra={"trigger_fired": trigger_fired},
        )

    except Exception as exc:
        trigger_context["errors"].append(str(exc))
        LOGGER.error("Stage 1 failed", extra={"error": str(exc)})
        raise

    finally:
        Path("trigger_context.json").write_text(
            json.dumps(trigger_context, indent=2),
            encoding="utf-8",
        )

        Path("stage1_debug.json").write_text(
            json.dumps(
                {
                    "assets_cfg": assets_cfg if "assets_cfg" in locals() else None,
                    "nti_cfg": nti_cfg if "nti_cfg" in locals() else None,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
