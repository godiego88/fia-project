import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from utils.logging import setup_logger
from utils.state import load_state, save_state, decay_state


LOGGER_NAME = "stage1-runner"
logger = setup_logger(LOGGER_NAME)


# =========================
# Configuration (Authoritative)
# =========================

DEFAULT_NTI_TRIGGER_THRESHOLD = 0.65
DEFAULT_NTI_REQUIRED_PERSISTENCE = 3
STATE_FILE = "state.json"
TRIGGER_CONTEXT_FILE = "trigger_context.json"


def get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Invalid float for {name}, using default")
        return default


def get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid int for {name}, using default")
        return default


# =========================
# Trigger Evaluation
# =========================

def evaluate_trigger(
    nti_value: float,
    persistence_count: int,
    threshold: float,
    required_persistence: int,
) -> bool:
    return nti_value >= threshold and persistence_count >= required_persistence


# =========================
# Trigger Context Builder
# =========================

def build_trigger_context(
    nti_value: float,
    quant_results: Dict[str, Any],
    nlp_results: Dict[str, Any],
    persistence_count: int,
) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "stage": 1,
        "triggered_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "nti": nti_value,
            "persistence_count": persistence_count,
        },
        "quant": quant_results,
        "nlp": nlp_results,
    }


def write_trigger_context(context: Dict[str, Any]) -> None:
    path = Path(TRIGGER_CONTEXT_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)
    logger.info("trigger_context.json written")


# =========================
# Main
# =========================

def main() -> None:
    logger.info("Stage 1 run started")

    nti_threshold = get_env_float(
        "NTI_TRIGGER_THRESHOLD",
        DEFAULT_NTI_TRIGGER_THRESHOLD,
    )
    nti_required_persistence = get_env_int(
        "NTI_REQUIRED_PERSISTENCE",
        DEFAULT_NTI_REQUIRED_PERSISTENCE,
    )

    state = load_state(STATE_FILE)

    # =========================
    # Data Acquisition (example placeholder)
    # =========================
    # Prices and text inputs are assumed to be fetched inside engines
    prices = pd.Series(dtype="float64")
    texts = []

    # =========================
    # Run Engines
    # =========================

    quant_results = run_quant_analysis(prices)
    nlp_results = run_nlp_analysis(texts)

    nti_value = float(quant_results.get("nti", 0.0))
    logger.info("NTI computed")

    # =========================
    # Persistence Logic
    # =========================

    if nti_value >= nti_threshold:
        state["persistence"] = state.get("persistence", 0) + 1
    else:
        state = decay_state(state)
        logger.info("Persistence decayed — resetting")

    save_state(STATE_FILE, state)
    persistence_count = state.get("persistence", 0)

    # =========================
    # Trigger Decision
    # =========================

    triggered = evaluate_trigger(
        nti_value,
        persistence_count,
        nti_threshold,
        nti_required_persistence,
    )

    if not triggered:
        logger.info("No trigger — silent exit")
        return

    logger.info("Stage 2 trigger condition met")

    trigger_context = build_trigger_context(
        nti_value=nti_value,
        quant_results=quant_results,
        nlp_results=nlp_results,
        persistence_count=persistence_count,
    )

    write_trigger_context(trigger_context)
    logger.info("Stage 1 completed successfully")


if __name__ == "__main__":
    main()
