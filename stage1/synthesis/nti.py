# stage1/synthesis/nti.py

from typing import Dict


def compute_nti(
    quant_scores: Dict[str, float],
    nlp_score: float,
    persistence_value: float,
) -> dict:
    """
    NTI = Normalized Trigger Index

    Design invariant:
    - NTI MUST ALWAYS RESOLVE
    - Empty quant input => NTI = 0.0 (hard conservative)
    - Stage 1 NEVER throws due to signal sparsity
    """

    # ---------- HARD SAFETY: EMPTY QUANT ----------
    if not quant_scores:
        nti_value = 0.0
        qualifies = False

        return {
            "nti": nti_value,
            "qualifies": qualifies,
            "components": {
                "quant": 0.0,
                "nlp": float(nlp_score),
                "persistence": float(persistence_value),
            },
            "reason": "no_quant_signal",
        }

    # ---------- NORMAL PATH ----------
    quant_component = sum(quant_scores.values()) / len(quant_scores)

    # Conservative weighted blend
    nti_value = (
        0.6 * quant_component +
        0.3 * nlp_score +
        0.1 * persistence_value
    )

    qualifies = nti_value >= 1.0  # threshold stays STRICT

    return {
        "nti": float(nti_value),
        "qualifies": bool(qualifies),
        "components": {
            "quant": float(quant_component),
            "nlp": float(nlp_score),
            "persistence": float(persistence_value),
        },
        "reason": "computed",
    }
