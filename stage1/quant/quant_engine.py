"""
Quantitative Analysis Engine

Implements canonical Stage 1 quantitative metrics
as defined in the FIA Quant & Classical NLP Math Canon.
"""

from typing import Dict, Any


def run_quant_analysis(prices: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Run quantitative analysis on market price inputs.

    Contract:
    - Every asset with status="ok" MUST emit a quant record
    - Failed assets emit explicit failure metadata
    - Empty return is ILLEGAL unless universe is empty
    """

    results: Dict[str, Dict[str, float]] = {}

    for symbol, payload in prices.items():
        if not isinstance(payload, dict):
            results[symbol] = {
                "status": "failed",
                "reason": "invalid_price_payload",
            }
            continue

        if payload.get("status") != "ok":
            results[symbol] = {
                "status": "failed",
                "reason": payload.get("reason", "price_unavailable"),
            }
            continue

        price = payload.get("latest_price")
        if price is None:
            results[symbol] = {
                "status": "failed",
                "reason": "missing_latest_price",
            }
            continue

        # Stage 1 canonical scalar quant metrics
        results[symbol] = {
            "status": "ok",
            "latest_price": float(price),
        }

    if not results:
        raise RuntimeError("Quant engine produced no outputs")

    return results
