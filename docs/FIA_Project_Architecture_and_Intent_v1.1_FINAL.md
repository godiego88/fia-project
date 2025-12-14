
# FIA PROJECT — ARCHITECTURE & INTENT
## Version 1.1 FINAL — LOCKED — NO CHANGES EVER

This document defines the **why**, **philosophy**, **system boundaries**, and **architectural intent** of the FIA Project.
It exists to ensure that *every implementation decision* remains aligned with the original purpose, constraints, and intelligence design.

This document pairs with:
- **Quant & Classical NLP Math Canon (LOCKED)**
- **LLM Prompt Canon (LOCKED)**
- **Execution Specification v1.1 FINAL**

If a choice conflicts with this document, the choice is invalid.

---

## 1. CORE INTENT (WHY THIS SYSTEM EXISTS)

The FIA Project exists to:

- Detect **non-obvious, non-trivial market states**
- Separate **signal from noise**, not summarize news
- Identify **fragility, regime change, and mispricing**
- Operate **silently by default**
- Escalate only when **structural conditions justify attention**

This is **not**:
- A trading bot
- A news summarizer
- A dashboard
- A prediction engine

It is an **automated market intelligence system**.

---

## 2. DESIGN PHILOSOPHY

### 2.1 Quant-Dominant by Construction
- Quantitative signals define *whether something matters*
- NLP provides *context*, not authority
- LLMs provide *direction and reasoning*, never computation

### 2.2 Silence Is a Feature
- No trigger = no output
- No output = success
- The system is designed to do *nothing* most of the time

### 2.3 Determinism Over Cleverness
- Every metric is reproducible
- Every random process is seeded
- Every artifact is schema-validated

### 2.4 Constraints Are First-Class
- 100% free compute
- GitHub Actions only
- API quotas actively enforced
- Degradation preferred over failure

---

## 3. TWO-STAGE INTELLIGENCE MODEL

### Stage 1 — Broad Intelligence Filter
Purpose:
- Scan widely
- Compute aggressively
- Discard ruthlessly

Characteristics:
- Runs 4× daily
- No LLM usage
- Heavy vectorized quant
- Classical NLP only
- Produces **trigger_context.json** or nothing

Stage 1 answers:
> “Is there anything here that deserves deeper thought?”

---

### Stage 2 — Deep Directed Reasoning
Purpose:
- Allocate scarce intelligence (APIs + LLM)
- Explore *why* something matters
- Stress-test narratives

Characteristics:
- Triggered only
- LLM-orchestrated
- Quant/NLP still compute-heavy
- LLM never computes
- Produces **deep_results.json**

Stage 2 answers:
> “What is actually happening, and why now?”

---

## 4. ROLE OF THE LLM (STRICTLY LIMITED)

The LLM is **not**:
- A calculator
- A signal generator
- A decision-maker

The LLM **is**:
1. **Orchestrator**
   - Decides what to zoom into
   - Allocates deeper computation
2. **Adversarial Critic**
   - Attempts to kill the signal
   - Forces robustness
3. **Synthesizer**
   - Converts evidence into structured reasoning

LLMs operate **only after quant/NLP evidence exists**.

---

## 5. DATA HIERARCHY (AUTHORITY ORDER)

From highest authority to lowest:

1. Quant stress & regime signals
2. Cross-asset behavior
3. Simulation tail risk
4. Classical NLP anomalies
5. LLM reasoning

If higher layers contradict lower layers, lower layers are ignored.

---

## 6. NON-TRIVIALITY AS A FIRST-CLASS CONCEPT

The system is built around **Non-Triviality**.

A signal is non-trivial only if:
- Multiple independent domains agree
- The condition persists
- The behavior deviates from recent regimes
- Alternative explanations fail

This is formalized in the **Non-Triviality Index (NTI)**.

---

## 7. FAILURE PHILOSOPHY

Failure modes are explicit and intentional.

Acceptable failures:
- No output
- Skipped APIs
- Degraded analysis
- Discarded signals

Unacceptable failures:
- False confidence
- Unjustified alerts
- Undocumented assumptions
- Silent schema violations

---

## 8. EMAIL AS A DELIVERY MECHANISM (NOT THE PRODUCT)

The email exists only to:
- Surface rare, high-value intelligence
- Provide human-readable synthesis
- Preserve attention

The email is **never** sent unless:
- Stage 1 triggers
- Stage 2 completes
- Adversarial critique passes

---

## 9. AUDITABILITY & TRUST

Every run must be:
- Replayable
- Explainable
- Auditable via artifacts

Trust comes from:
- Consistency
- Silence
- Being wrong *less often*, not faster

---

## 10. GOLDEN PRINCIPLES (UNBREAKABLE)

1. Silence beats noise
2. Quant beats narrative
3. Constraints sharpen intelligence
4. LLMs guide — they never decide
5. If unsure, do nothing

---

## 11. FINAL STATEMENT

This system is designed to think **less often**, but **better**.

If it speaks, it must deserve attention.

END OF DOCUMENT — VERSION 1.1 FINAL — NO CHANGES EVER
