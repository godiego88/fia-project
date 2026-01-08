import csv
import io
import urllib.request
from typing import List, Dict


class UniverseLoadError(RuntimeError):
    pass


def load_universe_from_google_sheets(cfg: Dict) -> List[str]:
    gs_cfg = cfg.get("google_sheets")
    if not gs_cfg:
        raise UniverseLoadError("google_sheets config missing")

    sheet_id = gs_cfg.get("sheet_id")
    worksheet = gs_cfg.get("worksheet")
    ticker_column = gs_cfg.get("ticker_column")

    if not sheet_id or not worksheet or not ticker_column:
        raise UniverseLoadError("Incomplete google_sheets configuration")

    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={worksheet}"
    )

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        raise UniverseLoadError(f"Failed to fetch Google Sheet CSV: {e}") from e

    reader = csv.DictReader(io.StringIO(raw))

    if ticker_column not in reader.fieldnames:
        raise UniverseLoadError(
            f"Ticker column '{ticker_column}' not found in sheet"
        )

    tickers = []
    for row in reader:
        val = row.get(ticker_column)
        if val:
            tickers.append(val.strip())

    expectations = cfg.get("expectations", {})
    if expectations.get("uppercase", True):
        tickers = [t.upper() for t in tickers]

    if expectations.get("deduplicate", True):
        tickers = list(set(tickers))

    if expectations.get("sort", True):
        tickers = sorted(tickers)

    min_size = gs_cfg.get("min_universe_size", 1)
    max_size = gs_cfg.get("max_universe_size")

    if len(tickers) < min_size:
        raise UniverseLoadError(
            f"Universe size {len(tickers)} below minimum {min_size}"
        )

    if max_size is not None and len(tickers) > max_size:
        raise UniverseLoadError(
            f"Universe size {len(tickers)} exceeds maximum {max_size}"
        )

    return tickers
