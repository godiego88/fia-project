
# FIA Quant & Classical NLP Math Canon (LOCKED)

## General Rules
- All metrics normalized to [0,1]
- All rolling windows use trading days
- Missing data ⇒ metric excluded, never imputed
- All calculations deterministic

---

## Quant Modules

### 1. Price Z-Score (Multi-Horizon)
For horizon h ∈ {1d,5d,20d,60d}

z_h = (P_t − mean(P_{t−h:t})) / std(P_{t−h:t})

Normalized:
z_norm = min(1, |z_h| / 4)

Final Price Stress Score:
Q_price = mean(z_norm across h)

---

### 2. Volatility Regime Shift
Realized vol:
σ_real = std(log returns, 20d)

Trailing vol:
σ_trail = EMA(σ_real, 60d)

Divergence:
Δσ = (σ_real − σ_trail) / σ_trail

Score:
Q_vol = clip((Δσ + 0.5) / 1.5, 0, 1)

Regime flag:
- Δσ > 0.4 → expansion
- Δσ < −0.3 → compression

---

### 3. Correlation Breakdown
Rolling correlation matrix (20d)
Compute average off-diagonal correlation C_t

ΔC = |C_t − mean(C_{t−60:t})|

Q_corr = clip(ΔC / 0.4, 0, 1)

---

### 4. Momentum vs Mean Reversion Stress
Momentum:
M = sign(P_t − SMA_60)

Short-term return r_5d

Stress if sign(r_5d) ≠ M

Q_mr = 1 if stress else 0

---

### 5. Monte Carlo Tail Risk
10,000 paths, geometric Brownian motion

Compute Expected Shortfall (5%)

Normalize:
Q_tail = clip(ES / |mean return|, 0, 1)

---

## NLP Modules (Classical Only)

### 1. TF-IDF + BM25 Relevance
Corpus = last 30d documents
Score document relevance to entity

N_relevance = mean(top 10 relevance scores)

---

### 2. Burst Detection
Daily doc count d_t
Baseline = mean(d_{t−30:t})

Burst score:
B = max(0, (d_t − baseline) / baseline)

N_burst = clip(B / 3, 0, 1)

---

### 3. Sentiment Stress
Lexicon polarity p_i
Vol-adjusted sentiment:

S = mean(p_i) * σ_real

N_sent = clip(|S| / 2, 0, 1)

---

### 4. Narrative Conflict
Cluster cosine distance between last 7d and prior 30d topics

N_conflict = clip(distance / 0.6, 0, 1)

---

## Aggregation

Quant score:
Q = mean(Q_price, Q_vol, Q_corr, Q_mr, Q_tail)

Narrative score:
N = mean(N_relevance, N_burst, N_sent, N_conflict)

