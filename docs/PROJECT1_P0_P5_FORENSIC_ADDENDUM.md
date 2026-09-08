# Project 1 — P0–P5 Forensic Statistical Addendum

**Date:** 2026-09-08  
**Frozen workflow:** `34206500727`  
**Model/provider:** `llama3.2:1b` / local Ollama  
**Primary metric:** official Spider execution accuracy  
**Evaluator:** `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`

## Verdict

The frozen artifacts are complete enough for primary P0–P5 inference. P6 remains blocked. P5 is a statistically robust regression against P0, not a near miss.

## Full 1,034-case results

| Policy | Correct | Accuracy | Wilson 95% CI | Mean cost | Median latency | P95 latency |
|---|---:|---:|---:|---:|---:|---:|
| P0 | 254 | 24.56% | 22.04–27.28% | 0.2691 | 2.001 s | 5.572 s |
| P1 | 0 | 0.00% | 0.00–0.37% | 0.0517 | 0.120 s | 0.135 s |
| P2 | 256 | 24.76% | 22.22–27.48% | 0.2687 | 1.540 s | 4.802 s |
| P3 | 256 | 24.76% | 22.22–27.48% | 0.2687 | 1.541 s | 4.788 s |
| P4 | 20 | 1.93% | 1.26–2.97% | 0.0849 | 0.121 s | 3.076 s |
| P5 | 123 | 11.90% | 10.06–14.01% | 0.2439 | 1.280 s | 11.536 s |

No policy reaches the predefined 90% reliability target.

## P5 vs P0: primary paired inference

Full 1,034 cases:

- P0-only correct: **158**
- P5-only correct: **27**
- Discordant pairs: **185**
- Accuracy delta P5−P0: **−12.67 percentage points**
- Exact two-sided McNemar p ≈ **1.0 × 10^-23**
- Paired bootstrap 95% CI for accuracy difference: approximately **[−15.09, −10.25] pp**
- Discordant-pair odds ratio favoring P0: **158/27 ≈ 5.85**

Disjoint 780-case development partition:

- P0: **193/780 = 24.74%**
- P5: **91/780 = 11.67%**
- Delta: **−13.08 pp**
- Exact McNemar p ≈ **6.5 × 10^-16**

254-case schema holdout:

- P0: **60/254 = 23.62%**
- P5: **32/254 = 12.60%**
- Delta: **−11.02 pp**
- Exact McNemar p ≈ **6.17 × 10^-5**
- Paired bootstrap 95% CI: approximately **[−16.14, −5.91] pp**

**Correction:** earlier project notes reported 61 P0-correct holdout cases. Direct recomputation of the frozen artifacts gives **60**.

## Multiple comparisons

For P0 vs P1–P5, Holm correction does not change the substantive conclusions: P1, P4 and P5 are significant degradations; P2 and P3 are not significant against P0 on the full paired benchmark.

## Baseline validity findings

### P2/P3 duplicate implementation

Current code sends both P2 and P3 through the same `query_complexity(State(question)) < 0.45` rule. Their identical outcomes are therefore expected. They should not be presented as independent routing baselines.

### P4 is not calibrated confidence

P4's confidence is a deterministic heuristic based on question length and the presence of `why`; it is not learned or calibrated. Its 1.93% full-set and 0.79% holdout accuracy should not be generalized to confidence routing in general.

## Efficiency frontier

P5 reduces mean synthetic action cost by approximately **9.35%** overall (0.2691 → 0.2439) and **7.20%** on holdout (0.2694 → 0.2500).

It also reduces mean LLM calls by approximately **27.2%**, input tokens by **24.2%**, and output tokens by **23.2%**.

However, these savings are not reliability-constrained improvements because accuracy falls by 12.67 pp overall and 11.02 pp on holdout.

Latency is tail-sensitive: P5's full-set median is lower, but its P95 is approximately **2.07× P0**. On holdout, P5's mean latency is approximately **1.53 s higher** than P0, with paired bootstrap CI approximately **[0.136, 3.317] s**, and P95 is approximately **1.85× P0**.

## P5 selector forensic finding

P5 did not escalate on **493/1,034 = 47.68%** of cases. Those 493 cases produced **zero official-correct answers**. P5 escalated on 541 cases and achieved 123/541 = **22.74%** accuracy there.

Among P0's 254 correct cases, **142 were P5 non-escalation cases**. This means the current trigger misses approximately **55.9% of P0's correct cases**. This is not a ground-truth escalation label, but it is strong evidence that the current selector is poorly aligned with downstream LLM success.

Within escalated cases, 96 are correct under both policies, 27 are P5-only successes, and 16 are P0-only successes. Escalation therefore both recovers and destroys correct answers.

## Failure taxonomy: full benchmark

| Policy | Correct | Semantic mismatch | Execution error | No output |
|---|---:|---:|---:|---:|
| P0 | 254 | 349 | 412 | 19 |
| P1 | 0 | 656 | 0 | 378 |
| P2 | 256 | 339 | 417 | 22 |
| P3 | 256 | 339 | 417 | 22 |
| P4 | 20 | 620 | 75 | 319 |
| P5 | 123 | 545 | 171 | 195 |

## Scientific interpretation

Established:

1. No P0–P5 policy reaches 90% reliability under the tested configuration.
2. P5 is materially and statistically worse than P0 on official execution accuracy.
3. The P5 regression persists on the schema-disjoint holdout.
4. P5 genuinely reduces model work and synthetic action cost.
5. P5 does not provide a reliable latency improvement; its tail is substantially worse.
6. The current evidence trigger is a poor selector for when LLM execution will succeed.

Not established:

- adaptive routing is ineffective in general;
- confidence routing is ineffective in general;
- stronger models would behave the same;
- the result generalizes beyond Spider/SQLite;
- P6 cannot work.

## P6 gate

**BLOCKED.**

Before any P6 implementation, establish three things prospectively:

1. whether the deterministic evidence stage is intrinsically useful or merely too weak;
2. whether the evidence features predict downstream LLM success;
3. whether any redesigned evidence operator can be frozen before evaluation without holdout leakage.

If no defensible unresolved mechanism remains, reframe the contribution around the empirical boundary and failure modes of evidence-dependent analytical execution rather than forcing a positive adaptive-routing claim.
