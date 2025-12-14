"""
FIA IO Utilities

Deterministic loaders for configuration and schema files.
This module performs parsing only — no validation, no defaults,
no side effects.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict


def _resolve_path(path: str) -> Path:
    """
    Resolve a relative path from the project root.
    """
    return Path(path).resolve()


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
