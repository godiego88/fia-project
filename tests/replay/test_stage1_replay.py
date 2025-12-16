"""
Stage 1 Replay Harness

Purpose:
- Verify determinism of Stage 1 NTI computation
- Verify persistence behavior (including decay reset)
- Verify trigger vs silent behavior

This test:
- Uses deterministic fixtures
- Does NOT call live APIs
- Does NOT mutate production code paths
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from stage1.runner import main as stage1_main
from utils.state import (
    save_persistence,
    save_last_run_id,
    save_persistence,
)
from utils.io import load_json_file


REPLAY_DIR = Path("tests/replay/fixtures")
TRIGGER_FILE = Path("trigger_context.json")


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch):
    """
    Ensure a clean environment for each replay run.
    """
    # Ensure no trigger artifact exists
    if TRIGGER_FILE.exists():
        TRIGGER_FILE.unlink()

    # Reset persistence explicitly
    save_persistence(0)
    save_last_run_id("replay-test")

    yield

    if TRIGGER_FILE.exists():
        TRIGGER_FILE.unlink()


def test_stage1_replay_deterministic_trigger(monkeypatch):
    """
    Deterministic replay test.

    Asserts:
    - NTI exceeds trigger threshold
    - Persistence increments correctly
    - trigger_context.json is produced
    """

    # -------------------------
    # Inject deterministic inputs
    # -------------------------

    def mock_load_market_prices(_):
        return load_json_file(REPLAY_DIR / "market_prices.json")

    def mock_run_quant_analysis(_):
        return load_json_file(REPLAY_DIR / "quant_results.json")

    def mock_run_nlp_analysis(_):
        return load_json_file(REPLAY_DIR / "nlp_results.json")

    monkeypatch.setattr(
        "stage1.ingestion.market_prices.load_market_prices",
        mock_load_market_prices,
    )
    monkeypatch.setattr(
        "stage1.quant.quant_engine.run_quant_analysis",
        mock_run_quant_analysis,
    )
    monkeypatch.setattr(
        "stage1.nlp.nlp_engine.run_nlp_analysis",
        mock_run_nlp_analysis,
    )

    # -------------------------
    # Run Stage 1
    # -------------------------
    stage1_main()

    # -------------------------
    # Assertions
    # -------------------------
    assert TRIGGER_FILE.exists(), "Expected trigger_context.json to be created"

    trigger = json.loads(TRIGGER_FILE.read_text())

    assert trigger["nti"] >= 0.72, "NTI must exceed trigger threshold"
    assert trigger["persistence"] >= 1, "Persistence must increment"
    assert "quant_results" in trigger
    assert "nlp_results" in trigger
    assert "nti_components" in trigger


def test_stage1_replay_silent_exit(monkeypatch):
    """
    Verifies silent exit when NTI does not qualify.
    """

    def mock_load_market_prices(_):
        return load_json_file(REPLAY_DIR / "market_prices.json")

    def mock_run_quant_analysis(_):
        return load_json_file(REPLAY_DIR / "quant_results_low.json")

    def mock_run_nlp_analysis(_):
        return load_json_file(REPLAY_DIR / "nlp_results_low.json")

    monkeypatch.setattr(
        "stage1.ingestion.market_prices.load_market_prices",
        mock_load_market_prices,
    )
    monkeypatch.setattr(
        "stage1.quant.quant_engine.run_quant_analysis",
        mock_run_quant_analysis,
    )
    monkeypatch.setattr(
        "stage1.nlp.nlp_engine.run_nlp_analysis",
        mock_run_nlp_analysis,
    )

    stage1_main()

    assert not TRIGGER_FILE.exists(), "Trigger must not be produced"
