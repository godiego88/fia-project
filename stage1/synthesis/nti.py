"""
NTI Synthesis Engine

Combines quantitative and NLP signals into a single
Normalized Tension Index (NTI).
"""

from typing import Dict


def compute_nti(
    *,
    quant_results: Dict,
    nlp_results: Dict,
    nti_cfg: Dict,
) -> Dict:
    if not quant_results:
        raise RuntimeError("NTI computation failed: quant_results empty")

    if not nlp_results:
        raise RuntimeError("NTI computation failed: nlp_results empty")

    quant_weight = nti_cfg["weights"]["quant"]
    nlp_weight = nti_cfg["weights"]["nlp"]

    # Simple deterministic aggregation (Stage 1 baseline)
    quant_score = sum(
        v["volatility"] for v in quant_results.values()
    ) / len(quant_results)

    nlp_score = sum(
        v["score"] for v in nlp_results.values()
    ) / len(nlp_results)

    nti_value = (quant_score * quant_weight) + (nlp_score * nlp_weight)

    qualifies = nti_value >= nti_cfg["qualifying_threshold"]

    return {
        "nti": float(nti_value),
        "qualifies": bool(qualifies),
        "components": {
            "quant_score": float(quant_score),
            "nlp_score": float(nlp_score),
            "weights": {
                "quant": quant_weight,
                "nlp": nlp_weight,
            },
        },
    }
