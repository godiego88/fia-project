"""
Institutional Quant Engine – Stage 1

Multi-resolution regime detection with temporal coherence.
No averages. Regime + anomaly driven.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


WINDOWS = {
    "short": 5,
    "medium": 20,
    "long": 60,
}


def _returns(series: pd.Series) -> pd.Series:
    return series.pct_change().dropna()


def _regime_score(returns: pd.Series, window: int) -> float:
    if len(returns) < window:
        return -1.0  # explicit penalty
    r = returns[-window:]
    mu = r.mean()
    vol = r.std()
    if vol == 0:
        return -1.0
    return float(mu / vol)


def run_quant_analysis(price_series: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    results: Dict[str, Dict[str, float]] = {}

    for asset, raw in price_series.items():
        try:
            series = pd.Series(raw).dropna()
            if len(series) < max(WINDOWS.values()):
                results[asset] = {"quant_valid": 0.0}
                continue

            rets = _returns(series)

            regimes = {
                name: _regime_score(rets, w)
                for name, w in WINDOWS.items()
            }

            signs = [np.sign(v) for v in regimes.values()]
            coherence = 1.0 if abs(sum(signs)) == 3 else -1.0

            results[asset] = {
                **{f"regime_{k}": v for k, v in regimes.items()},
                "regime_coherence": coherence,
                "quant_valid": 1.0,
            }

        except Exception:
            results[asset] = {"quant_valid": 0.0}

    return results
