"""
Universe Loader — Authoritative Source of Truth

Loads the securities universe from Google Sheets.
This file MUST remain intelligence-preserving.
"""

import csv
import io
import requests
from typing import List, Dict

# Public CSV export for the Universe tab
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1OWThg74PwCsAz4_OpJZ8ZKykJCe0Oa8dXnT4LDAt_js"
    "/gviz/tq?tqx=out:csv&sheet=Universe"
)

REQUIRED_COLUMNS = {"ticker", "status", "asset name", "asset class"}


def load_universe_from_google_sheets() -> List[Dict[str, str]]:
    response = requests.get(GOOGLE_SHEET_CSV_URL, timeout=15)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    raw_headers = reader.fieldnames or []
    headers = {h.strip().lower() for h in raw_headers}

    if not REQUIRED_COLUMNS.issubset(headers):
        raise RuntimeError(
            f"Universe sheet schema invalid. "
            f"Expected columns {REQUIRED_COLUMNS}, got {headers}"
        )

    universe: List[Dict[str, str]] = []

    for raw_row in reader:
        # normalize keys once (minimal but critical)
        row = {k.strip().lower(): (v or "").strip() for k, v in raw_row.items()}

        status = row["status"].lower()
        if status != "active":
            continue

        ticker = row["ticker"].upper()
        if not ticker:
            continue

        universe.append(
            {
                "ticker": ticker,
                "status": status,
                "asset_name": row["asset name"],
                "asset_class": row["asset class"],
            }
        )

    if not universe:
        raise RuntimeError("Universe resolved but no ACTIVE assets found")

    return universe
