"""
Quant Engine — Cross-sectional stress, tail risk, regime fracture
Institutional-grade, deterministic
"""

from typing import Dict
import numpy as np
import math


def _safe_std(x: np.ndarray) -> float:
    return float(np.std(x)) if len(x) > 1 else 0.0


def _z(x: np.ndarray) -> np.ndarray:
    s = _safe_std(x)
    return np.zeros_like(x) if s == 0 else (x - np.mean(x)) / s


def run_quant_analysis(market: Dict[str, dict]) -> Dict:
    prices = []
    tickers = []
    failures = 0

    for t, d in market.items():
        if d["status"] == "ok" and d["latest_price"] is not None:
            prices.append(float(d["latest_price"]))
            tickers.append(t)
        else:
            failures += 1

    if len(prices) < 6:
        return {"global": {"entropy": 0.0, "valid_assets": len(prices)}}

    p = np.array(prices)
    logp = np.log(p)

    z = _z(logp)
    abs_z = np.abs(z)

    dispersion = float(np.std(logp))
    tail_density = float(np.mean(abs_z > 2.5))
    extreme_density = float(np.mean(abs_z > 3.5))
    skew = float(np.mean(z ** 3))
    kurtosis = float(np.mean(z ** 4) - 3.0)
    span = float(np.max(logp) - np.min(logp))

    instability = (
        dispersion * 0.25 +
        tail_density * 0.30 +
        extreme_density * 0.20 +
        abs(skew) * 0.10 +
        max(0.0, kurtosis) * 0.15
    )

    coverage_penalty = (len(prices) / max(1, len(market))) ** 0.5
    entropy = instability * coverage_penalty

    return {
        "global": {
            "dispersion": dispersion,
            "tail_density": tail_density,
            "extreme_density": extreme_density,
            "skew": skew,
            "kurtosis": kurtosis,
            "regime_span": span,
            "valid_assets": len(prices),
            "failed_assets": failures,
            "entropy": entropy,
        },
        "cross_section": {
            t: {
                "z": float(zi),
                "abs_z": float(abs(zi)),
                "tail": abs(zi) > 2.5,
                "extreme": abs(zi) > 3.5,
            }
            for t, zi in zip(tickers, z)
        },
    }
