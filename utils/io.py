"""
FIA IO Utilities

Deterministic loaders and writers for configuration,
schemas, and escalation artifacts.

This module performs parsing and explicit IO only.
No validation, no defaults, no inference, no branching logic.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import uuid

from utils.state import save_last_run_id


# -------------------------
# Internal helpers
# -------------------------

def _resolve_path(path: str) -> Path:
    """
    Resolve a relative path from the project root.
    """
    return Path(path).resolve()


# -------------------------
# Public loaders
# -------------------------

def load_yaml_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    Args:
        path: Relative path to YAML file

    Returns:
        Parsed YAML content as a dictionary

    Raises:
        RuntimeError if file cannot be read or parsed
    """
    file_path = _resolve_path(path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load YAML config: {path}") from e

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise RuntimeError(f"YAML config must be a mapping: {path}")

    return data


def load_json_file(path: str) -> Dict[str, Any]:
    """
    Load a JSON file.

    Args:
        path: Relative path to JSON file

    Returns:
        Parsed JSON content as a dictionary

    Raises:
        RuntimeError if file cannot be read or parsed
    """
    file_path = _resolve_path(path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON file: {path}") from e


# -------------------------
# Escalation artifact writer
# -------------------------

def write_trigger_context(
    *,
    nti: float,
    nti_threshold: float,
    persistence_required: int,
    persistence_observed: int,
    components: Dict[str, Any],
    strong_components: list[str],
    quant_breakdown: Dict[str, float],
    nlp_breakdown: Dict[str, float],
    assets_analyzed: list[str],
    assets_excluded: list[str],
    reason_excluded: Dict[str, str],
    degradations: list[str],
    warnings: list[str],
) -> None:
    """
    Write Stage 1 trigger context to disk.

    This function is called ONLY after escalation
    conditions are already met. It performs no
    validation, inference, or branching.
    """

    run_id = str(uuid.uuid4())

    context = {
        "meta": {
            "run_id": run_id,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "stage": "stage1",
            "version": "1.1",
        },
        "decision": {
            "nti": nti,
            "nti_threshold": nti_threshold,
            "persistence_required": persistence_required,
            "persistence_observed": persistence_observed,
            "triggered": True,
        },
        "components": components,
        "component_flags": {
            "above_0_7": strong_components,
            "missing": [k for k, v in components.items() if v is None],
        },
        "quant_breakdown": quant_breakdown,
        "nlp_breakdown": nlp_breakdown,
        "data_coverage": {
            "assets_analyzed": assets_analyzed,
            "assets_excluded": assets_excluded,
            "reason_excluded": reason_excluded,
        },
        "notes": {
            "degradations": degradations,
            "warnings": warnings,
        },
    }

    with open("trigger_context.json", "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

    # HARD LINKAGE: persist run_id for auditability
    save_last_run_id(run_id)
