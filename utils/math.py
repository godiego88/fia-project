"""
Math utilities for FIA.

Shared numerical helpers.
"""

import numpy as np
from typing import Iterable


def clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return float(np.clip(value, low, high))


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(np.mean(values))
