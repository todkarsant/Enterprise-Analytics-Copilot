# P5 Mechanism Forensics — Gate A / Gate B Analysis

Date: 2026-09-08  
Branch: `research/p5-mechanism-forensics`  
Clean challenger run: `34219674022`  
Clean P5R head: `052468ac50df2c82eaeba351bbadbffdd8747a07`  
Provider: local Ollama (`llama3.2:1b`)  
Status: diagnostic analysis; no new inference and no holdout tuning

## 1. Purpose

This analysis is the next mechanism-level test in the original Project 1 research program. It does **not** replace the original research question and does not authorize P6.

The two questions are:

- **Gate A — evidence-stage validity:** Can the current deterministic evidence stage be treated as a correct terminal analytical action?
- **Gate B — selector signal:** Do label-free post-evidence features contain useful information about whether downstream LLM generation is likely to succeed?

The analysis uses the clean prospective P5R traces and pairs them with the already-frozen P0 outcomes. The four-schema holdout is evaluated only after the development analysis and is not used to tune any policy.

## 2. Gate A — current evidence-only termination fails

The strongest direct finding is that the current deterministic evidence stage is not a valid terminal correctness mechanism under the official Spider execution evaluator.

### Development partition: 1,034 cases

P5R non-escalated cases:

- n = 352
- official P5R correctness = **0/352 (0%)**
- P0 correctness within the same cases = **89/352 (25.28%)**
- P5R mean cost = 0.05693
- P5R mean LLM calls = 0

P5R escalated cases:

- n = 682
- official P5R correctness = **179/682 (26.25%)**
- P0 correctness within the same cases = **165/682 (24.19%)**
- P5R mean cost = 0.42224
- P5R mean LLM calls = 1.368

The key preservation result is that **89 of the 254 P0-correct development cases (35.04%) were placed on the P5R non-escalation path**, where P5R subsequently received zero official-correct outcomes.

### Holdout partition: 254 cases across four held-out schemas

P5R non-escalated cases:

- n = 108
- official P5R correctness = **0/108 (0%)**
- P0 correctness within the same cases = **33/108 (30.56%)**
- P5R mean cost = 0.05704
- P5R mean LLM calls = 0

P5R escalated cases:

- n = 146
- official P5R correctness = **41/146 (28.08%)**
- P0 correctness within the same cases = **27/146 (18.49%)**
- P5R mean cost = 0.44582
- P5R mean LLM calls = 1.445

The holdout preservation failure is stronger: **33 of 60 P0-correct holdout cases (55.00%) were non-escalated and therefore lost by the current P5R terminal decision.**

### Gate A interpretation

Gate A is therefore **FAILED for the current implementation**.

This does **not** prove that deterministic evidence is useless as an intermediate feature. It establishes the narrower and experimentally supported statement:

> The current deterministic evidence stage cannot safely terminate execution as if its evidence result were itself a correct answer.

This is consistent with the independent frozen P1 deterministic-only result of 0 official-correct cases on the full 1,034-case workload.

Any future policy must therefore treat deterministic execution as evidence generation or candidate generation, not as an automatically accepted final answer.

## 3. Gate B — evidence features contain predictive signal, but the current selector is not a calibrated reliability policy

The P5R trace contains label-free post-evidence features available before deciding whether to spend an LLM call, including:

- evidence reason category;
- evidence row count;
- evidence column count;
- escalation flag;
- generated-SQL presence/validity;
- execution status.

A diagnostic supervised test used **P0 official correctness as the downstream-success target**. This is an analysis target only; P0 labels were not exposed to the policy during inference.

### Development cross-validation

A logistic model using only `reason + evidence_row_count + evidence_column_count`, evaluated with 5-fold stratified cross-validation (seed 1729), achieved:

- ROC-AUC = **0.696**
- Average precision = **0.388**
- Brier score = **0.218**

Adding execution/generation status and escalation flag produced:

- ROC-AUC = **0.717**
- Average precision = **0.419**
- Brier score = **0.212**

These are diagnostic predictive results, not evidence of a deployable calibrated selector.

### Unseen-schema transfer

The `reason + row_count + column_count` model was fit only on the 780-case development partition and then evaluated once on the untouched 254-case holdout:

- ROC-AUC = **0.791**
- 20,000-case bootstrap 95% interval = **[0.731, 0.846]**
- Average precision = **0.510**
- Brier score = **0.191**

The signal therefore transfers to the four held-out schemas in this diagnostic test. This is evidence that the post-evidence state is **not information-free**.

However, predictive ranking is not equivalent to a reliability guarantee. The observed P0 prevalence on the holdout is only 23.62%, and no current policy approaches the 90%+ reliability targets specified by the research gate.

## 4. Selector category instability and preservation risk

Development P0 correctness varies materially across P5R evidence reasons:

| Evidence reason | n | P0 correctness |
|---|---:|---:|
| requested_name_not_projected | 172 | 26.74% |
| question_predicate_not_reflected | 160 | 23.13% |
| extremum_not_reflected | 102 | 16.67% |
| grouping_not_reflected | 91 | 10.99% |
| aggregation_not_reflected | 65 | 15.38% |
| literal_predicate_not_reflected | 62 | 46.77% |
| ordering_not_reflected | 30 | 53.33% |

The reason category is associated with P0 correctness on development data (chi-square p = 2.48e-08), but the categories do not form a calibrated probability scale.

On holdout data, category rates also shift materially. For example:

- `extremum_not_reflected`: 2.56% P0 correctness;
- `literal_predicate_not_reflected`: 63.64%;
- `requested_name_not_projected`: 15.15%.

This supports the conclusion that **the selector has signal but its hand-built binary escalation rule is not a reliability-calibrated decision rule**.

## 5. Paired outcome interpretation

P5R vs frozen P0:

### Development

- P5R correct: 179/1,034 = **17.31%**
- P0 correct: 254/1,034 = **24.56%**
- P0-only: 112
- P5R-only: 37
- accuracy delta: **−7.25 pp**
- exact McNemar p = **5.79e-10**
- paired mean cost delta P5R − P0 = **+0.02880**

### Holdout

- P5R correct: 41/254 = **16.14%**
- P0 correct: 60/254 = **23.62%**
- P0-only: 34
- P5R-only: 15
- accuracy delta: **−7.48 pp**
- exact McNemar p = **0.00940**
- paired mean cost delta P5R − P0 = **+0.01110**; bootstrap interval includes zero

P5R therefore improves materially over frozen P5, but still loses to P0 and does not deliver the intended cost advantage relative to P0.

## 6. Gate decision

| Gate | Result | Interpretation |
|---|---|---|
| A — current evidence-only terminal validity | **FAIL** | Deterministic evidence cannot safely terminate the task under the official evaluator. |
| B — evidence-state predictive signal | **PASS, diagnostic only** | Evidence features contain transferable ranking signal, but the current heuristic is not calibrated. |
| P5R vs P0 reliability/cost frontier | **FAIL** | P5R remains less accurate and is more expensive on mean cost. |
| P5R justification for P6 | **BLOCKED** | No evidence yet supports a new P6 policy claim. |

## 7. Consequence for the original research question

The original question remains unchanged: whether evidence-dependent analytical action selection can achieve a lower-cost reliability-constrained operating point than fixed strategies and strong post-evidence cascade baselines.

The present evidence narrows the mechanism diagnosis:

1. The **current deterministic terminal action is inadequate**.
2. The **post-evidence state contains predictive information** about downstream LLM success.
3. The **current selector does not convert that signal into reliable preservation** of cases the LLM can solve.
4. A prospective policy, if justified at all, must use evidence as a decision feature while protecting the incumbent/challenger relationship rather than unconditionally terminating or replacing outputs.
5. This remains insufficient to claim that P6 will outperform P0 or P5 at any reliability target.

## 8. P6 gate remains blocked

No P6 inference has been run or claimed from this analysis.

A P6 experiment is justified only if its decision rule is specified and frozen on the development partition before touching the holdout. Any future P6 must establish, prospectively:

- a predeclared acceptance/replacement rule;
- matched reliability evaluation against P0 and P5;
- cost measurement under the same accounting;
- timeout and failure accounting without denominator reduction;
- the four-schema holdout as an untouched final evaluation;
- ablation sufficient to distinguish evidence value from selector value.

If those conditions cannot yield a defensible reliability-constrained advantage, the project should reframe around the empirical boundary and failure modes rather than manufacture a positive routing result.
