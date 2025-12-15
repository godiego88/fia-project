"""
Persistent State Utilities

Minimal Supabase-backed persistence for Stage 1.
Stores NTI persistence counter and last triggering run_id.
"""

import os
from typing import Optional
from supabase import create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

PERSISTENCE_KEY = "nti_persistence"
RUN_ID_KEY = "last_run_id"


def _get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _load_int(key: str) -> int:
    client = _get_client()
    if client is None:
        return 0

    try:
        resp = (
            client
            .table("stage1_state")
            .select("value")
            .eq("key", key)
            .single()
            .execute()
        )
        if resp.data and "value" in resp.data:
            return int(resp.data["value"])
    except Exception:
        pass

    return 0


def _load_str(key: str) -> Optional[str]:
    client = _get_client()
    if client is None:
        return None

    try:
        resp = (
            client
            .table("stage1_state")
            .select("value")
            .eq("key", key)
            .single()
            .execute()
        )
        if resp.data and "value" in resp.data:
            return str(resp.data["value"])
    except Exception:
        pass

    return None


def _save(key: str, value) -> None:
    client = _get_client()
    if client is None:
        return

    try:
        (
            client
            .table("stage1_state")
            .upsert({"key": key, "value": value}, on_conflict="key")
            .execute()
        )
    except Exception:
        pass


# ---------- Public API ----------

def load_persistence() -> int:
    return _load_int(PERSISTENCE_KEY)


def save_persistence(value: int) -> None:
    _save(PERSISTENCE_KEY, int(value))


def load_last_run_id() -> Optional[str]:
    return _load_str(RUN_ID_KEY)


def save_last_run_id(run_id: str) -> None:
    _save(RUN_ID_KEY, run_id)
