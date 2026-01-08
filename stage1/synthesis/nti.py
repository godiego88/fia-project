import logging
from typing import Dict

logger = logging.getLogger("nti-engine")


def compute_nti(
    quant_signal: float,
    nlp_signal: float,
    nti_cfg: Dict,
) -> Dict:
    """
    Compute Normalized Threat Index (NTI).

    This function MUST:
    - Never assume missing config keys
    - Emit raw + normalized components
    - Stay compatible with final threshold schema
    """

    quant_cfg = nti_cfg.get("quant", {})
    nlp_cfg = nti_cfg.get("nlp", {})
    nti_meta = nti_cfg.get("nti", {})

    # ---- Normalization placeholders (Stage 2 will refine) ----
    quant_norm = float(quant_signal)
    nlp_norm = float(nlp_signal)

    method = nti_meta.get("method", "joint_extremity")

    if method == "joint_extremity":
        nti_score = abs(quant_norm) + abs(nlp_norm)
    else:
        raise ValueError(f"Unknown NTI method: {method}")

    return {
        "nti_score": nti_score,
        "components": {
            "quant_raw": quant_signal,
            "nlp_raw": nlp_signal,
            "quant_normalized": quant_norm,
            "nlp_normalized": nlp_norm,
        },
        "thresholds": {
            "qualifying": nti_meta.get("qualifying_score"),
            "trigger": nti_meta.get("trigger_score"),
        },
    }
