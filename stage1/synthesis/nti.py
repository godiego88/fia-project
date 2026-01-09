"""
Neural Tension Index (NTI)

Stage 1 intelligence synthesis.
Hard-gated, multiplicative signal as defined by project canon.

NTI is designed to:
- Fire rarely
- Be reproducible
- Encode joint evidence, not averages
"""

from __future__ import annotations
from typing import Dict, Any
import math


# -------------------------
# Canonical bounds (LOCKED)
# -------------------------
MAX_NTI = 1.0
MIN_NTI = 0.0

# Quant must cross this to be considered real signal
MIN_VALID_QUANT_STRENGTH = 0.15

# NLP is an amplifier, not a generator
MAX_NLP_MULTIPLIER = 1.25
MIN_NLP_MULTIPLIER = 0.75


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_nti(
    *,
    quant_results: Dict[str, Dict[str, float]],
    nlp_results: Dict[str, Any] | None,
    metadata: Dict[str, Any] | None = None,
) -> float:
    """
    Compute final NTI.

    HARD RULES:
    - No quant → NTI = 0
    - Weak quant → NTI = 0
    - NTI is multiplicative, never additive
    """

    # -------------------------
    # 1. QUANT EVIDENCE (REQUIRED)
    # -------------------------
    if not quant_results:
        return 0.0

    # Aggregate quant strength conservatively
    quant_strengths = []

    for symbol, metrics in quant_results.items():
        vol = metrics.get("volatility")
        mean_ret = metrics.get("mean_return")

        if vol is None or mean_ret is None or vol <= 0:
            continue

        # Signal-to-noise style normalization
        strength = abs(mean_ret) / vol
        quant_strengths.append(strength)

    if not quant_strengths:
        return 0.0

    # Median prevents single-asset distortion
    quant_strength = sorted(quant_strengths)[len(quant_strengths) // 2]

    if quant_strength < MIN_VALID_QUANT_STRENGTH:
        return 0.0

    Q = _clamp(quant_strength)

    # -------------------------
    # 2. NLP ALIGNMENT (AMPLIFIER)
    # -------------------------
    if not nlp_results:
        S = 1.0
    else:
        alignment = float(nlp_results.get("alignment_score", 0.0))
        confidence = float(nlp_results.get("confidence", 0.0))

        raw = 1.0 + (alignment * confidence)
        S = _clamp(raw, MIN_NLP_MULTIPLIER, MAX_NLP_MULTIPLIER)

    # -------------------------
    # 3. NOVELTY (ANTI-REPETITION)
    # -------------------------
    novelty = float(metadata.get("novelty", 1.0)) if metadata else 1.0
    N = _clamp(novelty)

    # -------------------------
    # 4. PERSISTENCE (ANTI-NOISE)
    # -------------------------
    persistence = float(metadata.get("persistence", 1.0)) if metadata else 1.0
    P = _clamp(persistence)

    # -------------------------
    # 5. FRAGILITY / RISK PENALTY
    # -------------------------
    fragility = float(metadata.get("fragility", 1.0)) if metadata else 1.0
    F = _clamp(fragility)

    # -------------------------
    # FINAL NTI (MULTIPLICATIVE)
    # -------------------------
    nti = Q * S * N * P * F

    # Numerical safety only — no softening
    nti = float(_clamp(nti, MIN_NTI, MAX_NTI))

    # Hard floor: if quant collapses, NTI collapses
    if nti < MIN_VALID_QUANT_STRENGTH:
        return 0.0

    return nti
