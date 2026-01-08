"""
Stage 1 Validation Contracts

Enforces structural and semantic validity of Stage 1 outputs.
NO inference. NO thresholds. NO scoring.
"""

from typing import Dict, Any


class ValidationError(RuntimeError):
    pass


def validate_quant_results(quant_results: Dict[str, Any]) -> None:
    if not isinstance(quant_results, dict) or not quant_results:
        raise ValidationError("Quant results must be a non-empty dict")

    for ticker, payload in quant_results.items():
        if "signals" not in payload:
            raise ValidationError(f"{ticker}: missing 'signals'")
        if "confidence" not in payload:
            raise ValidationError(f"{ticker}: missing 'confidence'")
        if not isinstance(payload["confidence"], (int, float)):
            raise ValidationError(f"{ticker}: confidence must be numeric")


def validate_nlp_results(nlp_results: Dict[str, Any]) -> None:
    if not isinstance(nlp_results, dict) or not nlp_results:
        raise ValidationError("NLP results must be a non-empty dict")

    required_fields = {"sentiment_score", "relevance_score", "confidence"}

    for ticker, payload in nlp_results.items():
        missing = required_fields - payload.keys()
        if missing:
            raise ValidationError(f"{ticker}: missing NLP fields {missing}")


def validate_nti_output(nti_result: Dict[str, Any]) -> None:
    required_keys = {"nti", "components", "qualifies"}

    missing = required_keys - nti_result.keys()
    if missing:
        raise ValidationError(f"NTI output missing keys {missing}")

    if not isinstance(nti_result["nti"], (int, float)):
        raise ValidationError("NTI value must be numeric")

    if not isinstance(nti_result["components"], dict):
        raise ValidationError("NTI components must be dict")

    if not isinstance(nti_result["qualifies"], bool):
        raise ValidationError("NTI qualifies flag must be boolean")
