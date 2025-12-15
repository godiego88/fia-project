"""
Classical NLP Relevance & Burst Module

Computes relevance and burstiness using deterministic,
frequency-based classical NLP methods.

Canon reference:
- N_relevance
- N_burst
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List
from collections import Counter


def relevance_burst_signal(
    documents: List[List[str]],
    baseline_documents: List[List[str]],
) -> float:
    """
    Compute relevance and burst signal.

    Args:
        documents: Current window of tokenized documents
        baseline_documents: Historical baseline tokenized documents

    Returns:
        Normalized relevance/burst signal ∈ [0,1]
    """
    if not documents or not baseline_documents:
        return 0.0

    current_tokens = [token for doc in documents for token in doc]
    baseline_tokens = [token for doc in baseline_documents for token in doc]

    if not current_tokens or not baseline_tokens:
        return 0.0

    current_counts = Counter(current_tokens)
    baseline_counts = Counter(baseline_tokens)

    scores = []

    for token, curr_freq in current_counts.items():
        base_freq = baseline_counts.get(token, 0)

        if base_freq == 0:
            continue

        burst_ratio = curr_freq / base_freq
        scores.append(burst_ratio)

    if not scores:
        return 0.0

    # Normalize burst score into [0,1]
    raw_score = sum(scores) / len(scores)
    return min(max(raw_score, 0.0), 1.0)
