"""
Classical NLP Conflict Detection Module

Detects contradictory signals via simultaneous presence
of opposing sentiment tokens.

Canon reference:
- N_conflict
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List

from stage1.nlp.sentiment import POSITIVE_WORDS, NEGATIVE_WORDS


def conflict_signal(documents: List[List[str]]) -> float:
    """
    Compute conflict / contradiction signal.

    Args:
        documents: Tokenized documents

    Returns:
        Normalized conflict signal ∈ [0,1]
    """
    if not documents:
        return 0.0

    pos_count = 0
    neg_count = 0

    for doc in documents:
        for token in doc:
            if token in POSITIVE_WORDS:
                pos_count += 1
            elif token in NEGATIVE_WORDS:
                neg_count += 1

    total = pos_count + neg_count
    if total == 0:
        return 0.0

    conflict = 1.0 - abs(pos_count - neg_count) / total

    return min(max(conflict, 0.0), 1.0)
