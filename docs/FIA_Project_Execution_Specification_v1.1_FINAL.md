
# FIA PROJECT — EXECUTION SPECIFICATION v1.1 FINAL
NO CHANGES EVER

This document supersedes v1.0 and incorporates:
- Locked Quant/NLP math canon
- Locked LLM prompt canon
- Final orchestration logic

---

## Stage 1 — Quant + Classical NLP Engine

Runs 4× daily on GitHub Actions.

Steps:
1. Check Supabase resource ledger
2. Skip APIs ≥95% usage
3. Fetch market, macro, news data
4. Compute quant tensors
5. Compute NLP tensors
6. Compute NTI

NTI Formula:
NTI = 0.30Q + 0.20S + 0.20N + 0.15P + 0.15F

Trigger:
NTI ≥ 0.72 for ≥2 consecutive runs

Output:
trigger_context.json

---

## Stage 2 — LLM-Orchestrated Intelligence

Triggered ONLY if Stage 1 fires.

Flow:
1. Orchestrator selects focus
2. Directed deep quant recomputation
3. Directed deep NLP recomputation
4. Adversarial critique
5. Final synthesis

Abort conditions:
- Critic kills signal
- Data quality < 80%
- LLM schema violation

---

## Final Output

deep_results.json
Email sent ONLY if Stage 2 completes successfully.

Email contains:
- Executive summary
- Quant evidence
- Narrative evidence
- Confidence & uncertainty

---

## Golden Rule

Silence is success.
Noise is failure.

END OF FILE.
