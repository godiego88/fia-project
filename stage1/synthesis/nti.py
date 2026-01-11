"""
NTI Synthesis – Canonical Stage 1

Hard-gated, sparse, regime-based NTI with:
- Temporal acceleration
- Cross-asset topology
- Multi-resolution coherence
"""

from typing import Dict
import numpy as np
import networkx as nx


def _penalty() -> float:
    return -1.0


def compute_nti(
    quant_results: Dict[str, Dict[str, float]],
    nlp_results: Dict[str, Dict[str, float]],
) -> Dict[str, float]:

    assets = set(quant_results) & set(nlp_results)
    if not assets:
        return {"nti": 0.0, "trigger": 0.0}

    G = nx.Graph()
    for a in assets:
        G.add_node(a)

    # topology via regime agreement
    for a in assets:
        for b in assets:
            if a >= b:
                continue
            qa = quant_results[a]
            qb = quant_results[b]
            if qa.get("regime_coherence") == qb.get("regime_coherence"):
                G.add_edge(a, b)

    cluster_bonus = (
        max(len(c) for c in nx.connected_components(G)) / len(assets)
        if G.number_of_edges() > 0
        else 0.0
    )

    nti_components = []

    for a in assets:
        q = quant_results[a]
        n = nlp_results[a]

        if q.get("quant_valid") != 1.0 or n.get("nlp_valid") != 1.0:
            nti_components.append(_penalty())
            continue

        if q["regime_coherence"] < 0 or n["nlp_coherence"] < 0:
            nti_components.append(_penalty())
            continue

        base = (
            q["regime_short"]
            + q["regime_medium"]
            + q["regime_long"]
            + n["sentiment_short"]
            + n["sentiment_long"]
        )

        nti_components.append(base)

    nti_raw = float(np.mean(nti_components))
    nti = nti_raw * cluster_bonus

    # temporal derivatives (deterministic placeholders, persisted across runs later)
    d_nti = nti_raw
    dd_nti = np.sign(d_nti) * abs(d_nti)

    trigger = 1.0 if abs(nti) > 1.5 and abs(dd_nti) > 0.5 else 0.0

    return {
        "nti": float(nti),
        "delta_nti": float(d_nti),
        "delta2_nti": float(dd_nti),
        "cluster_bonus": float(cluster_bonus),
        "trigger": trigger,
    }
