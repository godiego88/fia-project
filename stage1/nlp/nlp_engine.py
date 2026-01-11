"""
Institutional NLP Engine – Stage 1

Multi-horizon sentiment regimes.
Hard agreement gating.
"""

from typing import List, Dict
import numpy as np


HORIZONS = {
    "short": 7,
    "long": 30,
}


def run_nlp_analysis(universe: List[str]) -> Dict[str, Dict[str, float]]:
    results: Dict[str, Dict[str, float]] = {}

    for asset in universe:
        # deterministic placeholder for sentiment vectors
        # (real model plugs here without changing interface)
        sentiment_short = np.tanh(len(asset) % 7 - 3)
        sentiment_long = np.tanh(len(asset) % 11 - 5)

        coherence = 1.0 if np.sign(sentiment_short) == np.sign(sentiment_long) else -1.0

        results[asset] = {
            "sentiment_short": float(sentiment_short),
            "sentiment_long": float(sentiment_long),
            "nlp_coherence": coherence,
            "nlp_valid": 1.0,
        }

    return results
