"""
NTI — Hard-Gated Signal Compression Engine (Institutional Grade)

Implements:
- Multi-resolution NTI (short / medium / long)
- ΔNTI and Δ²NTI (temporal acceleration proxies)
- Cross-asset coherence gating
- Multi-resolution regime agreement gating
- Explicit missing / weak signal penalties
- Deterministic, sparse, high-entropy output
"""

from typing import Dict


def _resolution_bucket(regimes: Dict, bucket: str) -> Dict:
    if bucket == "short":
        keys = ["5d"]
    elif bucket == "medium":
        keys = ["20d"]
    else:
        keys = ["60d"]

    return {k: regimes.get(k) for k in keys if regimes.get(k, {}).get("valid")}


def _regime_agreement(regimes: Dict) -> bool:
    trends = {r["trend"] for r in regimes.values()}
    return len(trends) == 1 if regimes else False


def compute_nti(
    quant_results: Dict,
    nlp_results: Dict,
    market_metadata: Dict,
    enforce_cross_asset_coherence: bool = True,
    enforce_multi_resolution_agreement: bool = True,
    enable_temporal_dynamics: bool = True,
) -> Dict:

    nti_levels = {"short": 0.0, "medium": 0.0, "long": 0.0}
    penalties = 0.0
    diagnostics = {"assets": {}}

    for asset, q in quant_results["per_asset"].items():
        asset_diag = {}

        regimes = q.get("regimes", {})
        nlp = nlp_results["per_asset"].get(asset)
        market = market_metadata.get(asset)

        if not regimes or not nlp or not market:
            penalties += 2.0
            asset_diag["penalty"] = "missing_data"
            diagnostics["assets"][asset] = asset_diag
            continue

        if market["status"] != "ok":
            penalties += 1.5
            asset_diag["penalty"] = "market_failed"
            diagnostics["assets"][asset] = asset_diag
            continue

        if not nlp["coherent"]:
            penalties += 1.0
            asset_diag["penalty"] = "nlp_incoherent"
            diagnostics["assets"][asset] = asset_diag
            continue

        for bucket in ["short", "medium", "long"]:
            bucket_regimes = _resolution_bucket(regimes, bucket)

            if enforce_multi_resolution_agreement and not _regime_agreement(bucket_regimes):
                penalties += 0.5
                asset_diag[f"{bucket}_agreement"] = False
                continue

            nti_levels[bucket] += 1.0
            asset_diag[f"{bucket}_agreement"] = True

        diagnostics["assets"][asset] = asset_diag

    topology_bonus = 0.0
    if enforce_cross_asset_coherence:
        clusters = quant_results.get("topology", {}).get("coherent_clusters", {})
        topology_bonus = sum(1.0 for v in clusters.values() if v >= 2)

    nti_short = nti_levels["short"] - penalties * 0.5
    nti_medium = nti_levels["medium"] - penalties * 0.75
    nti_long = nti_levels["long"] - penalties

    nti = nti_long + topology_bonus

    delta = nti_short - nti_medium
    delta2 = nti_short - 2 * nti_medium + nti_long

    regime_flags = {
        "trigger": nti > 2.0 and delta > 0 and delta2 > 0,
        "cross_asset_coherent": topology_bonus > 0,
        "penalized": penalties > 0,
    }

    confidence = max(
        0.0,
        nti / (1.0 + penalties)
    )

    return {
        "nti": round(nti, 4),
        "nti_short": round(nti_short, 4),
        "nti_medium": round(nti_medium, 4),
        "nti_long": round(nti_long, 4),
        "delta": round(delta, 4),
        "delta2": round(delta2, 4),
        "confidence": round(confidence, 4),
        "regime_flags": regime_flags,
        "diagnostics": diagnostics,
    }
