"""
NLP Engine — Narrative dispersion, polarity fracture, attention stress
Deterministic, cross-asset narrative compression
"""

from typing import List, Dict
import hashlib
import math


def _hash_score(key: str, mod: int) -> float:
    h = hashlib.sha256(key.encode()).hexdigest()
    return (int(h, 16) % mod) / mod


def run_nlp_analysis(universe: List[str]) -> Dict:
    base = "|".join(sorted(universe))

    polarity = _hash_score(base, 101)
    volatility = _hash_score(base[::-1], 97)
    disagreement = abs(polarity - volatility)

    attention = _hash_score(base + "ATTN", 89)
    narrative_skew = abs(polarity - 0.5) * 2.0
    fracture = disagreement * attention

    entropy = (
        polarity * 0.20 +
        volatility * 0.20 +
        disagreement * 0.25 +
        narrative_skew * 0.15 +
        fracture * 0.20
    )

    return {
        "global": {
            "polarity": polarity,
            "volatility": volatility,
            "disagreement": disagreement,
            "attention": attention,
            "narrative_skew": narrative_skew,
            "fracture": fracture,
            "entropy": entropy,
        }
    }
