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
    trend = int(np.sign(mean))

    z = (r.iloc[-1] - r.mean()) / (r.std() + 1e-9)

    return {
        "valid": True,
        "mean": float(mean),
        "vol": float(vol),
        "trend": trend,
        "zscore": float(z),
    }


def run_quant_analysis(
    prices: Dict[str, List[float]],
    windows: List[int] = WINDOWS,
    detect_regimes: bool = True,
    detect_anomalies: bool = True,
    build_cross_asset_stats: bool = True,
) -> dict:
    # ---- HARD INPUT VALIDATION ----
    series: Dict[str, pd.Series] = {}
    for ticker, price_series in prices.items():
        if not isinstance(price_series, list) or len(price_series) < max(windows):
            continue
        series[ticker] = pd.Series(price_series)

    returns = {k: _returns(s) for k, s in series.items()}

    per_asset = {}
    for ticker, r in returns.items():
        regimes = {f"{w}d": _regime_stats(r, w) for w in windows}

        # ---- Trend break: sign flip across resolutions ----
        trends = [
            regimes[f"{w}d"]["trend"]
            for w in windows
            if regimes[f"{w}d"]["valid"]
        ]
        trend_break = len(set(trends)) > 1 if trends else False

        # ---- Volatility structure ----
        vols = {
            f"{w}d": regimes[f"{w}d"]["vol"]
            for w in windows
            if regimes[f"{w}d"]["valid"]
        }

        # ---- Deterministic anomaly ----
        anomaly = detect_anomalies and any(
            abs(regimes[f"{w}d"].get("zscore", 0)) > 3
            for w in windows
            if regimes[f"{w}d"]["valid"]
        )

        per_asset[ticker] = {
            "regimes": regimes,
            "trend_break": trend_break,
            "volatility_structure": vols,
            "anomaly": anomaly,
        }

    # ---- Cross-asset topology ----
    topology = {}
    if build_cross_asset_stats and len(returns) > 1:
        df = pd.DataFrame(returns).dropna()
        corr = df.corr()

        topology = {
            "correlation": corr.to_dict(),
            "coherent_clusters": (
                (corr.abs() > 0.6).sum(axis=1)
            ).to_dict(),
        }

    return {
        "per_asset": per_asset,
        "topology": topology,
    }
