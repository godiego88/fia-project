"""
FIA IO Utilities

Deterministic loaders for configuration and schema files.
Deterministic writers for Stage 1 trigger artifacts.

This module performs parsing and writing only:
- no validation
- no defaults
- no branching logic
"""

import json
import yaml
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ---------- internal helpers ----------

def _resolve_path(path: str) -> Path:
    """
    Resolve a relative path from the project root.
    """
    return Path(path).resolve()


# ---------- loaders ----------

def load_yaml_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.
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
    """
    file_path = _resolve_path(path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON file: {path}") from e


# ---------- writers ----------

def write_trigger_context(
    *,
    nti: float,
    nti_threshold: float,
    persistence_required: int,
    persistence_observed: int,
    components: Dict[str, Any],
    strong_components: List[str],
    quant_breakdown: Dict[str, float],
    nlp_breakdown: Dict[str, float],
    assets_analyzed: List[str],
    assets_excluded: List[str],
    reason_excluded: Dict[str, str],
    degradations: List[str],
    warnings: List[str],
) -> None:
    """
    Write Stage 1 trigger context to disk.

    Called ONLY after escalation conditions are met.
    No validation. No interpretation.
    """

    context = {
        "meta": {
            "run_id": str(uuid.uuid4()),
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
