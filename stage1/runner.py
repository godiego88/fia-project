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
from typing import Dict

import pandas as pd

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


def _safe_float(value) -> float:
    """
    Convert pandas / numpy scalars to float safely.
    Fixes FutureWarning properly.
    """
    if isinstance(value, pd.Series):
        return float(value.iloc[0])
    return float(value)


def _synthesize_nti_components(
    quant_results: Dict,
    nlp_results: Dict,
) -> Dict[str, float]:
    """
    Synthesize canonical NTI components (Q, S, N, P, F)
    from Stage 1 quant + NLP outputs.

    NTI math and triggering remain fully inside nti.py.
    """

    components: Dict[str, float] = {}

    # Q — Quantitative stress proxy (mean volatility, normalized)
    vol_values = [
        _safe_float(v["volatility"])
        for v in quant_results.values()
        if isinstance(v, dict) and "volatility" in v
    ]
    components["Q"] = min(1.0, sum(vol_values) / len(vol_values)) if vol_values else 0.0

    # S — Structural signal (not yet implemented → neutral, explicit)
    components["S"] = 0.0

    # N — NLP anomaly signal (max normalized score)
    nlp_values = [
        _safe_float(v)
        for v in nlp_results.values()
        if isinstance(v, (int, float))
    ]
    components["N"] = max(nlp_values) if nlp_values else 0.0

    # P — Persistence proxy (handled canonically inside NTI)
    components["P"] = 0.0

    # F — Fragility proxy (not yet implemented → neutral, explicit)
    components["F"] = 0.0

    return components


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
    # NTI component synthesis
    # -------------------------
    components = _synthesize_nti_components(
        quant_results=quant_results,
        nlp_results=nlp_results,
    )

    # -------------------------
    # Persistence (pre-NTI)
    # -------------------------
    persistence = load_persistence()

    if should_reset_persistence(now):
        LOGGER.info("Persistence decayed — resetting")
        persistence = 0

    # -------------------------
    # NTI computation (CANONICAL)
    # -------------------------
    nti_value, trigger, updated_persistence = compute_nti(
        components=components,
        persistence_count=persistence,
    )

    save_persistence(updated_persistence)

    LOGGER.info(
        "NTI computed",
        extra={
            "nti": nti_value,
            "trigger": trigger,
            "components": components,
            "persistence": updated_persistence,
        },
    )

    # -------------------------
    # Trigger handling
    # -------------------------
    if trigger:
        mark_qualifying_run(now)
        LOGGER.warning("Stage 2 trigger condition met")

        trigger_context = {
            "run_id": run_id,
            "timestamp_utc": now.isoformat(),
            "nti": nti_value,
            "persistence": updated_persistence,
            "components": components,
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
