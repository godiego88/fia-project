"""
FIA Stage 2 Orchestrator

Consumes Stage 1 trigger context and performs
LLM-orchestrated deep research per canon.
"""

import json
import os
import requests
from typing import Dict

from utils.io import load_json_file
from governance.quota_manager import is_allowed


PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

if not PERPLEXITY_API_KEY:
    raise RuntimeError("PERPLEXITY_API_KEY must be set")


def _call_perplexity(system_prompt: str, user_payload: Dict) -> Dict:
    """
    Execute a single Perplexity call with quota enforcement.
    """

    if not is_allowed("perplexity"):
        raise RuntimeError("Perplexity quota >=95%; Stage 2 execution blocked")

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0.2,
    }

    resp = requests.post(
        PERPLEXITY_ENDPOINT,
        headers=headers,
        json=body,
        timeout=60,
    )
    resp.raise_for_status()

    return resp.json()


def run_stage2() -> None:
    trigger_context = load_json_file("trigger_context.json")

    orchestrator_out = _call_perplexity(
        system_prompt=(
            "You are the Strategic Orchestrator. "
            "Decide whether this signal is worth deeper investigation."
        ),
        user_payload=trigger_context,
    )

    critic_out = _call_perplexity(
        system_prompt=(
            "You are the Adversarial Critic. "
            "Attempt to invalidate or weaken the signal."
        ),
        user_payload={
            "trigger": trigger_context,
            "orchestrator": orchestrator_out,
        },
    )

    final_out = _call_perplexity(
        system_prompt=(
            "You are the Final Synthesizer. "
            "Explain causality, uncertainty, and regime implications."
        ),
        user_payload={
            "trigger": trigger_context,
            "orchestrator": orchestrator_out,
            "critic": critic_out,
        },
    )

    with open("deep_results.json", "w", encoding="utf-8") as f:
        json.dump(final_out, f, indent=2)


if __name__ == "__main__":
    run_stage2()
