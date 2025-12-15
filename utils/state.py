"""
Persistent State Utilities

Provides minimal persistence for Stage 1 across executions.
Currently supports NTI persistence counter only.
"""

import os
from supabase import create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

STATE_KEY = "nti_persistence"


def _get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def load_persistence() -> int:
    """
    Load NTI persistence counter.
    Defaults to 0 on any failure.
    """
    client = _get_client()
    if client is None:
        return 0

    try:
        resp = (
            client
            .table("stage1_state")
            .select("value")
            .eq("key", STATE_KEY)
            .single()
            .execute()
        )

        if resp.data and "value" in resp.data:
            return int(resp.data["value"])
    except Exception:
        pass

    return 0


def save_persistence(value: int) -> None:
    """
    Save NTI persistence counter.
    Fails silently.
    """
    client = _get_client()
    if client is None:
        return

    try:
        (
            client
            .table("stage1_state")
            .upsert(
                {"key": STATE_KEY, "value": int(value)},
                on_conflict="key",
            )
            .execute()
        )
    except Exception:
        pass
