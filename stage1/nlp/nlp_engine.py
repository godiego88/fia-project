"""
NLP Engine

Narrative pressure detector.
"""

from typing import List, Dict
import random


def run_nlp_analysis(universe: List[str]) -> Dict[str, dict]:
    results = {}

    for ticker in universe:
        sentiment = random.uniform(-1, 1)
        intensity = abs(sentiment)

        results[ticker] = {
            "sentiment": sentiment,
            "intensity": intensity,
        }

    return results
