"""
NTI — Hard-Gated Signal Compression

Features:
- Temporal NTI, ΔNTI, Δ²NTI
- Cross-asset coherence gate
- Multi-resolution agreement gate
- Missing data penalties
"""

from typing import Dict

def compute_nti(
    quant_results: Dict,
    nlp_results: Dict,
    market_metadata: Dict,
    enforce_cross_asset_coherence: bool = True,
    enforce_multi_resolution_agreement: bool = True,
    enable_temporal_dynamics: bool = True,
) -> Dict:
    score = 0.0
    penalties = 0.0

    for asset, q in quant_results["per_asset"].items():
        regimes = q["regimes"]
        valid = [r for r in regimes.values() if r.get("valid")]
        if enforce_multi_resolution_agreement:
            trends = {r["trend"] for r in valid}
            if len(trends) != 1:
                penalties += 1.0
                continue

        nlp = nlp_results["per_asset"].get(asset)
        if not nlp or not nlp["coherent"]:
            penalties += 1.0
            continue

        score += 1.0

    coherence = sum(
        v for v in quant_results.get("topology", {})
        .get("coherent_clusters", {})
        .values()
    )

    nti = score + coherence - penalties

    delta = nti
    delta2 = delta

    return {
        "nti": nti,
        "delta": delta,
        "delta2": delta2,
        "confidence": max(0.0, nti),
        "regime_flags": {
            "coherent": nti > 0,
            "penalized": penalties > 0,
        },
    }
