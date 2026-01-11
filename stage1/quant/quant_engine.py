"""
Quant Engine — Multi-Resolution Regime + Topology

Outputs:
- Per-asset regimes (5d / 20d / 60d)
- Trend breaks, volatility structure
- Cross-asset correlation graph
- Deterministic anomaly flags
"""

from typing import Dict, List
import pandas as pd
import numpy as np

WINDOWS = [5, 20, 60]

def _returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change().dropna()

def _regime_stats(r: pd.Series, w: int) -> dict:
    if len(r) < w:
        return {"valid": False}
    rw = r.rolling(w)
    vol = rw.std().iloc[-1]
    mean = rw.mean().iloc[-1]
    trend = np.sign(mean)
    return {
        "valid": True,
        "mean": float(mean),
        "vol": float(vol),
        "trend": int(trend),
        "zscore": float((r.iloc[-1] - r.mean()) / (r.std() + 1e-9)),
    }

def run_quant_analysis(
    prices: Dict[str, float],
    windows: List[int] = WINDOWS,
    detect_regimes: bool = True,
    detect_anomalies: bool = True,
    build_cross_asset_stats: bool = True,
) -> dict:
    series = {}
    for k, v in prices.items():
        series[k] = pd.Series(v if isinstance(v, list) else [v])

    returns = {k: _returns(s) for k, s in series.items()}

    per_asset = {}
    for k, r in returns.items():
        regimes = {f"{w}d": _regime_stats(r, w) for w in windows}
        anomaly = any(
            abs(regimes[f"{w}d"].get("zscore", 0)) > 3
            for w in windows if regimes[f"{w}d"]["valid"]
        )
        per_asset[k] = {
            "regimes": regimes,
            "anomaly": anomaly,
        }

    topology = {}
    if build_cross_asset_stats and len(returns) > 1:
        df = pd.DataFrame(returns).dropna()
        corr = df.corr()
        topology = {
            "correlation": corr.to_dict(),
            "coherent_clusters": (
                corr.abs() > 0.6
            ).sum(axis=1).to_dict(),
        }

    return {
        "per_asset": per_asset,
        "topology": topology,
    }
