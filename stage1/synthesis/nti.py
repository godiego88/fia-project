"""
NTI — Nonlinear Trigger Index
Agreement-gated, regime-aware, sparse by construction
"""

from typing import Dict
import math

TRIGGER_THRESHOLD = 0.90
MIN_DOMAIN_ENTROPY = 0.45


def compute_nti(*, quant_results: Dict, nlp_results: Dict) -> Dict:
    q = quant_results.get("global", {})
    n = nlp_results.get("global", {})

    q_e = float(q.get("entropy", 0.0))
    n_e = float(n.get("entropy", 0.0))

    if q_e < MIN_DOMAIN_ENTROPY or n_e < MIN_DOMAIN_ENTROPY:
        entropy = 0.0
        agreement = 0.0
    else:
        agreement = max(0.0, 1.0 - abs(q_e - n_e))
        entropy = (q_e * n_e) ** 0.5 * agreement

    trigger = entropy >= TRIGGER_THRESHOLD
    confidence = min(1.0, entropy * 1.8)

    regime = (
        "systemic_break"
        if q.get("extreme_density", 0.0) > 0.15 and n_e > 0.65
        else "stress"
        if entropy > 0.70
        else "normal"
    )

    return {
        "quant_entropy": q_e,
        "nlp_entropy": n_e,
        "agreement": agreement,
        "entropy": entropy,
        "confidence": confidence,
        "regime": regime,
        "trigger": trigger,
    }
