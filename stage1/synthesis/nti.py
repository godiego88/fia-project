"""
NTI — Narrative Tension Index

Final compression layer.
Triggers MUST be rare, reproducible, high-entropy.
"""

from typing import Dict


NTI_TRIGGER_THRESHOLD = 3.5


def compute_nti(
    quant_results: Dict[str, dict],
    nlp_results: Dict[str, dict],
    market_data: Dict[str, dict],
) -> dict:

    composite_scores = {}

    for ticker, q in quant_results.items():
        nlp = nlp_results.get(ticker)
        if not nlp:
            continue

        score = (
            q["score"] *
            (1 + abs(nlp["sentiment"])) *
            nlp["intensity"]
        )

        composite_scores[ticker] = score

    if not composite_scores:
        nti_value = 0.0
    else:
        nti_value = max(composite_scores.values())

    trigger = nti_value >= NTI_TRIGGER_THRESHOLD

    return {
        "nti": nti_value,
        "trigger": trigger,
        "threshold": NTI_TRIGGER_THRESHOLD,
        "top_contributors": sorted(
            composite_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5],
    }
