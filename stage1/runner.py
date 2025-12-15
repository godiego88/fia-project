"""
FIA Stage 1 Runner

Authoritative orchestration entry point for Stage 1.
Runs quant + classical NLP, computes NTI, and exits silently
unless escalation conditions are met.
"""

from stage1.ingestion.market_prices import fetch_market_prices

from stage1.quant.price_zscore import price_zscore_signal
from stage1.quant.volatility_regime import volatility_regime_signal
from stage1.quant.correlation_breakdown import correlation_breakdown_signal
from stage1.quant.mean_reversion import mean_reversion_signal
from stage1.quant.tail_risk import tail_risk_signal

from stage1.synthesis.quant_aggregate import aggregate_q
from stage1.synthesis.nlp_aggregate import aggregate_n
from stage1.synthesis.nti import compute_nti

from utils.state import load_persistence, save_persistence
from utils.io import load_yaml_config


def run_stage1() -> None:
    """
    Execute Stage 1 pipeline.
    """
    prices = fetch_market_prices()
    if not prices:
        return

    config = load_yaml_config("config/nt_thresholds.yaml")

    horizons = config.get("price_horizons", [])
    vol_realized = config.get("vol_realized_window", 20)
    vol_ema = config.get("vol_ema_window", 20)
    mr_window = config.get("mean_reversion_window", 20)
    corr_window = config.get("correlation_window", 20)

    q_components = {}

    # Compute per-asset price signals
    price_scores = []
    vol_scores = []
    mr_scores = []
    tail_scores = []

    for series in prices.values():
        price_scores.append(price_zscore_signal(series, horizons))
        vol_scores.append(volatility_regime_signal(series, vol_realized, vol_ema))
        mr_scores.append(mean_reversion_signal(series, mr_window))
        tail_scores.append(tail_risk_signal(series))

    if price_scores:
        q_components["Q_price"] = sum(price_scores) / len(price_scores)
    if vol_scores:
        q_components["Q_vol"] = sum(vol_scores) / len(vol_scores)
    if mr_scores:
        q_components["Q_mr"] = sum(mr_scores) / len(mr_scores)
    if tail_scores:
        q_components["Q_tail"] = sum(tail_scores) / len(tail_scores)

    # Correlation requires multi-asset input
    q_components["Q_corr"] = correlation_breakdown_signal(prices, corr_window)

    Q = aggregate_q(q_components)

    # NLP components intentionally omitted until ingestion exists
    N = aggregate_n({})

    components = {
        "Q": Q,
        "N": N,
        # S, P, F intentionally absent (canonical degradation)
    }

    persistence = load_persistence()
    nti, trigger, updated_persistence = compute_nti(components, persistence)
    save_persistence(updated_persistence)

    if trigger:
        # Trigger context emission handled by Stage 2 workflow
        return


if __name__ == "__main__":
    run_stage1()
