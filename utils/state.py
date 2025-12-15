"""
Persistent State Utilities

Supabase-backed persistence for Stage 1.
Tracks NTI persistence and last qualifying run timestamp.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Supabase credentials must be set")


PERSISTENCE_KEY = "nti_persistence"
LAST_RUN_TS_KEY = "last_qualifying_run_ts"
LAST_RUN_ID_KEY = "last_run_id"

DECAY_WINDOW = timedelta(hours=24)


def _get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def _load(key: str) -> Optional[str]:
    client = _get_client()
    resp = (
        client
        .table("stage1_state")
        .select("value")
        .eq("key", key)
        .single()
        .execute()
    )
    if resp.data:
        return resp.data["value"]
    return None


def _save(key: str, value: str) -> None:
    client = _get_client()
    client.table("stage1_state").upsert(
        {"key": key, "value": value},
        on_conflict="key",
    ).execute()


# -------------------------
# Persistence API
# -------------------------

def load_persistence() -> int:
    raw = _load(PERSISTENCE_KEY)
    if raw is None:
        return 0
    return int(raw)


def save_persistence(value: int) -> None:
    _save(PERSISTENCE_KEY, str(value))


def load_last_run_id() -> Optional[str]:
    return _load(LAST_RUN_ID_KEY)


def save_last_run_id(run_id: str) -> None:
    _save(LAST_RUN_ID_KEY, run_id)


def _load_last_timestamp() -> Optional[datetime]:
    raw = _load(LAST_RUN_TS_KEY)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def _save_timestamp(ts: datetime) -> None:
    _save(LAST_RUN_TS_KEY, ts.isoformat())


def should_reset_persistence(now: datetime) -> bool:
    """
    Determine whether persistence should decay.

    Persistence resets if the last qualifying run
    is outside the decay window.
    """
    last_ts = _load_last_timestamp()
    if last_ts is None:
        return True

    return (now - last_ts) > DECAY_WINDOW


def mark_qualifying_run(now: datetime) -> None:
    """
    Record the timestamp of a qualifying Stage 1 run.
    """
    _save_timestamp(now)
