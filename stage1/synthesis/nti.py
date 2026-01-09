from typing import Dict


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_nti(
    quant_results: Dict,
    nlp_results: Dict,
    persistence_value: int,
    nti_cfg: Dict,
) -> Dict:
    """
    Canonical NTI computation.
    """

    # --- Quant normalization ---
    quant_scores = []
    for v in quant_results.values():
        if "volatility" in v:
            quant_scores.append(v["volatility"])

    if not quant_scores:
        raise RuntimeError("NTI: no quant scores")

    quant_raw = sum(quant_scores) / len(quant_scores)
    quant_norm = _clamp(
        (quant_raw - nti_cfg["quant"]["min"]) /
        (nti_cfg["quant"]["max"] - nti_cfg["quant"]["min"])
    )

    # --- NLP normalization ---
    nlp_scores = [v.get("score") for v in nlp_results.values() if "score" in v]

    if not nlp_scores:
        raise RuntimeError("NTI: no NLP scores")

    nlp_raw = sum(nlp_scores) / len(nlp_scores)
    nlp_norm = _clamp(
        (nlp_raw - nti_cfg["nlp"]["min"]) /
        (nti_cfg["nlp"]["max"] - nti_cfg["nlp"]["min"])
    )

    # --- Persistence normalization ---
    persistence_norm = _clamp(
        persistence_value / nti_cfg["persistence"]["max"]
    )

    # --- Weighted aggregation ---
    weights = nti_cfg["weights"]

    nti = _clamp(
        weights["quant"] * quant_norm +
        weights["nlp"] * nlp_norm +
        weights["persistence"] * persistence_norm
    )

    qualifies = (
        quant_norm >= nti_cfg["quant"]["qualify_min"] and
        nlp_norm >= nti_cfg["nlp"]["qualify_min"]
    )

    return {
        "nti": nti,
        "components": {
            "quant": quant_norm,
            "nlp": nlp_norm,
            "persistence": persistence_norm,
        },
        "qualifies": qualifies,
    }
