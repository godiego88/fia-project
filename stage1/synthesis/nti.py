"""
Non-Triviality Index (NTI) computation

Authoritative implementation aligned with:
- FIA_Quant_NLP_Math_Canon
- FIA_Project_Execution_Specification_v1.1_FINAL

Pure function:
- No I/O
- No persistence
- No logging
"""

from typing import Dict


def _validate_cfg(nti_cfg: dict) -> None:
    if nti_cfg.get("locked") is not True:
        raise RuntimeError("NTI config is not locked")

    weights = nti_cfg.get("weights")
    if not weights:
        raise RuntimeError("NTI weights missing")

    required_weights = {"quant", "stress", "narrative", "persistence", "flow"}
    if set(weights.keys()) != required_weights:
        raise RuntimeError(f"NTI weights mismatch: expected {required_weights}")

    if not abs(sum(weights.values()) - 1.0) < 1e-6:
        raise RuntimeError("NTI weights must sum to 1.0")

    trigger = nti_cfg.get("trigger")
    if not trigger:
        raise RuntimeError("NTI trigger section missing")

    if "nti_min_value" not in trigger or "required_consecutive_runs" not in trigger:
        raise RuntimeError("NTI trigger thresholds incomplete")


def _normalize(value: float, cfg: dict) -> float:
    if value is None:
        raise RuntimeError("Cannot normalize None value")

    if not isinstance(value, (int, float)):
        raise RuntimeError("NTI component must be numeric")

    min_v = cfg["range_min"]
    max_v = cfg["range_max"]

    if max_v <= min_v:
        raise RuntimeError("Invalid NTI normalization range")

    normalized = (value - min_v) / (max_v - min_v)

    if cfg.get("enforce_clipping", True):
        normalized = max(min(normalized, 1.0), 0.0)

    return float(normalized)


def compute_nti(
    quant_results: Dict,
    nlp_results: Dict,
    persistence_value: int,
    nti_cfg: dict,
) -> dict:
    """
    Compute composite NTI and qualification flag.

    Expected inputs:
    - quant_results: dict with pre-aggregated quant metrics
    - nlp_results: dict with pre-aggregated NLP metrics
    - persistence_value: integer persistence counter
    - nti_cfg: locked NTI configuration

    Returns:
    {
        "nti": float,
        "components": {
            "quant": float,
            "stress": float,
            "narrative": float,
            "persistence": float,
            "flow": float,
        },
        "qualifies": bool
    }
    """

    _validate_cfg(nti_cfg)

    weights = nti_cfg["weights"]
    norm_cfg = nti_cfg["normalization"]
    trigger_cfg = nti_cfg["trigger"]

    # --- Component extraction (explicit, no inference) ---
    try:
        quant_raw = quant_results["aggregate_quant"]
        stress_raw = quant_results["aggregate_stress"]
        flow_raw = quant_results["aggregate_flow"]
    except KeyError as e:
        raise RuntimeError(f"Missing quant component: {e}")

    try:
        narrative_raw = nlp_results["aggregate_narrative"]
    except KeyError as e:
        raise RuntimeError(f"Missing NLP component: {e}")

    persistence_raw = float(persistence_value)

    # --- Normalization ---
    quant = _normalize(quant_raw, norm_cfg)
    stress = _normalize(stress_raw, norm_cfg)
    narrative = _normalize(narrative_raw, norm_cfg)
    persistence = _normalize(persistence_raw, norm_cfg)
    flow = _normalize(flow_raw, norm_cfg)

    components = {
        "quant": quant,
        "stress": stress,
        "narrative": narrative,
        "persistence": persistence,
        "flow": flow,
    }

    # --- Composite NTI ---
    nti = (
        quant * weights["quant"]
        + stress * weights["stress"]
        + narrative * weights["narrative"]
        + persistence * weights["persistence"]
        + flow * weights["flow"]
    )

    nti = float(nti)

    # --- Qualification ---
    qualifies = nti >= trigger_cfg["nti_min_value"]

    return {
        "nti": nti,
        "components": components,
        "qualifies": qualifies,
    }
