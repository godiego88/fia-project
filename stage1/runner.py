"""
Stage 1 Runner — High-Entropy Signal Compression Engine

Authoritative orchestration layer.
This runner is intentionally INTELLIGENCE-DENSE.
"""

import json
import logging
from datetime import datetime, timezone

from stage1.ingestion.universe_loader import load_universe_from_google_sheets
from stage1.ingestion.market_prices import load_market_prices
from stage1.quant.quant_engine import run_quant_analysis
from stage1.nlp.nlp_engine import run_nlp_analysis
from stage1.synthesis.nti import compute_nti

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("stage1-runner")


def main() -> None:
    LOGGER.info("Stage 1 started")

    # ------------------------------------------------------------------
    # 1. Universe resolution (STRUCTURED, AUTHORITATIVE)
    # ------------------------------------------------------------------
    universe = load_universe_from_google_sheets()
    if not universe:
        raise RuntimeError("Universe resolution failed")

    tickers = [u["ticker"] for u in universe]

    # ------------------------------------------------------------------
    # 2. Market ingestion (NO SILENT DROPS)
    # ------------------------------------------------------------------
    market = load_market_prices(tickers)

    prices = {
        ticker: data["price_series"]
        for ticker, data in market.items()
        if data["status"] == "ok" and data["price_series"] is not None
    }

    if not prices:
        LOGGER.error("No valid price series available — proceeding with full penalty")

    # ------------------------------------------------------------------
    # 3. Quant engine (multi-resolution, topology-aware)
    # ------------------------------------------------------------------
    quant = run_quant_analysis(
        prices=prices,
        windows=[5, 20, 60],
        detect_regimes=True,
        detect_anomalies=True,
        build_cross_asset_stats=True,
    )

    # ------------------------------------------------------------------
    # 4. NLP engine (STRUCTURED UNIVERSE — FIXED)
    # ------------------------------------------------------------------
    nlp = run_nlp_analysis(
        universe=universe,
        short_horizon_days=7,
        long_horizon_days=45,
        detect_sentiment_shifts=True,
        cluster_topics=True,
    )

    # ------------------------------------------------------------------
    # 5. NTI synthesis — HARD GATED
    # ------------------------------------------------------------------
    nti = compute_nti(
        quant_results=quant,
        nlp_results=nlp,
        market_metadata=market,
        enforce_cross_asset_coherence=True,
        enforce_multi_resolution_agreement=True,
        enable_temporal_dynamics=True,
    )

    # ------------------------------------------------------------------
    # 6. Emission (ALWAYS)
    # ------------------------------------------------------------------
    timestamp = datetime.now(timezone.utc).isoformat()

    with open("trigger_context.json", "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "nti": nti["nti"],
                "nti_delta": nti["delta"],
                "nti_acceleration": nti["delta2"],
                "regime_flags": nti["regime_flags"],
                "confidence": nti["confidence"],
            },
            f,
            indent=2,
        )

    with open("stage1_debug.json", "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "universe": universe,
                "market": market,
                "prices": prices,
                "quant": quant,
                "nlp": nlp,
                "nti_full": nti,
            },
            f,
            indent=2,
        )

    LOGGER.info("Stage 1 completed successfully")


if __name__ == "__main__":
    main()
