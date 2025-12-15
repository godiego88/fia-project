"""
Quantitative Signal Aggregation

Aggregates individual Q components into a single
quantitative score per the FIA Math Canon.

Canon reference:
- Q = mean(Q_price, Q_vol, Q_corr, Q_mr, Q_tail)
- All metrics ∈ [0,1]
- Missing data excluded
"""

from typing import Dict


def aggregate_q(components: Dict[str, float]) -> float:
    """
    Aggregate quantitative components into Q.

    Args:
        components: Mapping of component name -> value

    Returns:
        Aggregated Q score ∈ [0,1]
    """
    values = []

    for value in components.values():
        if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
            values.append(float(value))

    if not values:
        return 0.0

    return sum(values) / len(values)
