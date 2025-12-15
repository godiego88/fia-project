"""
Classical NLP Sentiment Polarity Module

Computes sentiment strength using a deterministic
lexicon-based approach.

Canon reference:
- N_sent
- All outputs ∈ [0,1]
- Deterministic, missing data excluded
"""

from typing import List


# Minimal, deterministic sentiment lexicon
POSITIVE_WORDS = {
    "gain", "gains", "up", "positive", "bull", "bullish",
    "strong", "growth", "optimistic", "surge", "rally"
}

NEGATIVE_WORDS = {
    "loss", "losses", "down", "negative", "bear", "bearish",
    "weak", "decline", "pessimistic", "drop", "crash"
}


def sentiment_signal(documents: List[List[str]]) -> float:
    """
    Compute sentiment polarity signal.

    Args:
        documents: Tokenized documents

    Returns:
        Normalized sentiment signal ∈ [0,1]
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

    imbalance = abs(pos_count - neg_count) / total

    # Already normalized to [0,1]
    return min(max(imbalance, 0.0), 1.0)
