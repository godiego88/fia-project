"""
Non-Triviality Index (NTI) Computation

Implements the canonical NTI formula and triggering rules
defined in FIA Math Canon and Execution Specification v1.1 FINAL.
"""

from typing import Dict, Tuple


NTI_WEIGHTS = {
    "Q": 0.30,
    "S": 0.20,
    "N": 0.20,
    "P": 0.15,
    "F": 0.15,
}

COMPONENT_THRESHOLD = 0.7
NTI_TRIGGER_THRESHOLD = 0.72
MIN_COMPONENTS_ABOVE_THRESHOLD = 3


def compute_nti(
    components: Dict[str, float],
    persistence_count: int,
) -> Tuple[float, bool, int]:
    """
    Compute NTI and evaluate triggering conditions.

    Args:
        components: Mapping of component name -> value (Q, S, N, P, F)
        persistence_count: Number of consecutive runs where
                           conditions have been met previously

    Returns:
        Tuple:
            nti_value (float): Computed NTI score
            trigger (bool): Whether Stage 2 should be triggered
            updated_persistence_count (int)
    """
    nti = 0.0
    valid_components = 0

    for name, weight in NTI_WEIGHTS.items():
        value = components.get(name)
        if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
            nti += weight * value
            valid_components += 1

    # Count strong components
    strong_components = sum(
        1 for v in components.values()
        if isinstance(v, (int, float)) and v >= COMPONENT_THRESHOLD
    )

    # Check non-triviality conditions
    conditions_met = (
        nti >= NTI_TRIGGER_THRESHOLD
        and strong_components >= MIN_COMPONENTS_ABOVE_THRESHOLD
    )

    if conditions_met:
        persistence_count += 1
    else:
        persistence_count = 0

    trigger = conditions_met and persistence_count >= 2

    return nti, trigger, persistence_count
