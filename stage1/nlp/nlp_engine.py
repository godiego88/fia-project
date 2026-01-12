"""
NLP Engine — Temporal + Cross-Asset Sentiment

Outputs:
- Short / long horizon sentiment per asset
- Temporal sentiment shifts
- Cross-asset coherence flags
- Deterministic topic clusters
"""

from typing import List, Dict
import hashlib


def _deterministic_score(key: str, horizon: str) -> float:
    """
    Deterministic pseudo-sentiment score in [-1, 1]
    """
    h = hashlib.sha256(f"{key}:{horizon}".encode()).hexdigest()
    return (int(h[:8], 16) % 2000) / 1000.0 - 1.0


def _topic_bucket(key: str) -> str:
    """
    Deterministic topic cluster assignment
    """
    h = hashlib.md5(key.encode()).hexdigest()
    buckets = ["macro", "rates", "equities", "crypto", "geopolitics"]
    return buckets[int(h[:2], 16) % len(buckets)]


def run_nlp_analysis(
    universe: List[Dict[str, str]],
    short_horizon_days: int = 7,
    long_horizon_days: int = 45,
    detect_sentiment_shifts: bool = True,
    cluster_topics: bool = True,
) -> dict:
    per_asset = {}
    topic_clusters: Dict[str, List[str]] = {}

    for asset in universe:
        ticker = asset["ticker"]

        short = _deterministic_score(ticker, "short")
        long = _deterministic_score(ticker, "long")
        shift = short - long

        coherent = abs(shift) > 0.25 and (short * long) > 0

        per_asset[ticker] = {
            "short": round(short, 4),
            "long": round(long, 4),
            "shift": round(shift, 4),
            "coherent": coherent,
        }

        if cluster_topics:
            topic = _topic_bucket(ticker)
            topic_clusters.setdefault(topic, []).append(ticker)

    global_sentiment = round(
        sum(v["shift"] for v in per_asset.values()), 4
    )

    temporal_shifts = {
        k: v["shift"]
        for k, v in per_asset.items()
        if abs(v["shift"]) > 0.4
    }

    return {
        "per_asset": per_asset,
        "global_sentiment": global_sentiment,
        "temporal_shifts": temporal_shifts,
        "topic_clusters": topic_clusters,
    }
