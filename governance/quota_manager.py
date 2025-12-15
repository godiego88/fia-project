"""
FIA Quota Manager

Authoritative read-only access layer for the Supabase resource ledger.
Enforces the Execution Specification rule:
- Skip APIs at >=95% usage.

This module MUST run before any external API calls.
"""

import os
from typing import Dict

from supabase import create_client, Client


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")


def _get_client() -> Client:
    """
    Create a Supabase client using the service role key.
    The service role key bypasses RLS by design (Supabase behavior).
    """
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_usage_ratios() -> Dict[str, float]:
    """
    Fetch all resources from the ledger and compute usage ratios.

    Returns:
        Dict[str, float]: resource_name -> usage_ratio (0.0–1.0)
    """
    client = _get_client()

    response = (
        client
        .table("resource_ledger")
        .select("resource_name, used_units, max_units")
        .execute()
    )

    if response.data is None:
        raise RuntimeError("Failed to fetch resource ledger")

    usage: Dict[str, float] = {}

    for row in response.data:
        used = float(row["used_units"])
        max_units = float(row["max_units"])

        if max_units <= 0:
            # Invalid configuration; safely ignored per degradation rules
            continue

        usage[row["resource_name"]] = used / max_units

    return usage


def is_allowed(resource_name: str, threshold: float = 0.95) -> bool:
    """
    Determine whether a resource is allowed to be used.

    Rule (Execution Specification v1.1 FINAL):
    - Skip APIs >=95% usage
    """
    usage = get_usage_ratios()

    if resource_name not in usage:
        # Unknown resources are allowed (degradation over failure)
        return True

    return usage[resource_name] < threshold
