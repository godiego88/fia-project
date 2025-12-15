"""
NLP Signal Aggregation

Aggregates individual N components into a single
N score per the FIA Math Canon.

Canon reference:
- N = mean(N_relevance, N_burst, N_sent, N_conflict)
- All metrics ∈ [0,1]
- Missing data excluded
"""

from typing import Dict


def aggregate_n(components: Dict[str, float]) -> float:
    """
    Aggregate NLP components into N.

    Args:
        components: Mapping of component name -> value

    Returns:
        Aggregated N score ∈ [0,1]
    """
    values = []

    for value in components.values():
        if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
            values.append(float(value))

    if not values:
        return 0.0

    return sum(values) / len(values)
