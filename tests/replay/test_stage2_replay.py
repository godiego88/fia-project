"""
Stage 2 Replay Harness

Purpose:
- Re-run Stage 2 using an existing trigger_context.json
- Verify schema compliance
- Verify presence and stability of critical decision fields

This test does NOT assert semantic equivalence of LLM output.
It enforces structural, contractual, and explainability guarantees.
"""

import json
import subprocess
from pathlib import Path

from jsonschema import validate, ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRIGGER_CONTEXT = PROJECT_ROOT / "trigger_context.json"
DEEP_RESULTS = PROJECT_ROOT / "deep_results.json"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "deep_results.schema.json"


def test_stage2_replay():
    # -------------------------
    # Preconditions
    # -------------------------
    assert TRIGGER_CONTEXT.exists(), (
        "trigger_context.json not found. "
        "Replay requires an existing Stage 1 trigger artifact."
    )

    # Remove previous output if it exists
    if DEEP_RESULTS.exists():
        DEEP_RESULTS.unlink()

    # -------------------------
    # Execute Stage 2
    # -------------------------
    result = subprocess.run(
        ["python", "stage2/orchestrator.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        "Stage 2 execution failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # -------------------------
    # Output existence
    # -------------------------
    assert DEEP_RESULTS.exists(), (
        "deep_results.json was not created by Stage 2 replay."
    )

    # -------------------------
    # Load outputs
    # -------------------------
    with open(DEEP_RESULTS, "r", encoding="utf-8") as f:
        deep_results = json.load(f)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # -------------------------
    # Schema validation
    # -------------------------
    try:
        validate(instance=deep_results, schema=schema)
    except ValidationError as e:
        raise AssertionError(
            f"Schema validation failed during replay:\n{e}"
        )

    # -------------------------
    # Critical field checks
    # -------------------------
    final = deep_results["final_assessment"]

    assert final["signal_status"] in {
        "confirmed",
        "weakened",
        "rejected",
    }, "Invalid signal_status"

    assert final["confidence_level"] in {
        "low",
        "medium",
        "high",
    }, "Invalid confidence_level"

    assert final["recommended_attention"] in {
        "monitor",
        "watchlist",
        "escalate",
    }, "Invalid recommended_attention"

    assert isinstance(final["explanation"], str) and final["explanation"].strip(), (
        "Final explanation must be a non-empty string"
    )
