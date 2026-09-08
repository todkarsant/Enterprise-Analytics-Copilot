# P5 Mechanism Forensic Result — Clean P5R Evidence

Date: 2026-09-08  
Clean challenger run: `34219674022`  
Clean P5R head: `052468ac50df2c82eaeba351bbadbffdd8747a07`  
Model/provider: `llama3.2:1b` / local Ollama  
Status: diagnostic result; no new inference after the clean P5R rerun

## 1. Primary conclusion

The clean prospective P5R experiment separates two effects that were confounded in the original P5 result:

1. The **current deterministic evidence stage is not valid as a terminal correctness mechanism** under the official Spider execution evaluator.
2. The **post-evidence state does contain predictive information** about downstream LLM success, but the current hand-built selector does not convert that information into a reliable preservation policy.

P5R improves official execution accuracy over frozen P5, but it remains substantially below frozen P0 and is more expensive on mean cost. Therefore the evidence does **not** justify a P6 performance claim.

The detailed Gate A/B analysis is documented in `docs/P5_GATE_A_B_FORENSIC_ANALYSIS.md`.

## 2. Frozen P0/P5 baseline and clean P5R

Full 1,034-case development workload:

| Policy | Official correct | Accuracy | Mean cost |
|---|---:|---:|---:|
| P0 | 254/1,034 | 24.56% | 0.26908 |
| P5 | 123/1,034 | 11.90% | 0.24393 |
| P5R | 179/1,034 | 17.31% | 0.29788 |

P5R vs P5:
- both correct: 83
- P5-only: 40
- P5R-only: 96
- accuracy delta: **+5.42 percentage points**
- exact McNemar p = **1.74e-06**
- paired mean cost delta P5R − P5 = **+0.05396**

P5R vs P0:
- both correct: 142
- P0-only: 112
- P5R-only: 37
- accuracy delta: **−7.25 percentage points**
- exact McNemar p = **5.79e-10**
- paired mean cost delta P5R − P0 = **+0.02880**

Thus the challenger recovers a substantial portion of the P5 accuracy loss but does not recover P0 performance and does not preserve P5's cost advantage.

## 3. Schema-disjoint evaluation

The defensible reporting split is:

- 780 cases across 16 non-holdout schemas: development partition.
- 254 cases across four held-out schemas: unseen-schema partition.

The four holdout schemas were also present in the complete 1,034-case artifact; therefore the full artifact must not be described as an independent test set. The holdout is a schema-disjoint evaluation only when policy/model decisions were frozen without using those schemas or their outcomes.

Holdout results:

| Policy | Official correct | Accuracy | Mean cost |
|---|---:|---:|---:|
| P0 | 60/254 | 23.62% | 0.26941 |
| P5 | 32/254 | 12.60% | 0.25000 |
| P5R | 41/254 | 16.14% | 0.28051 |

P5R vs P0:
- P0-only: 34
- P5R-only: 15
- accuracy delta: **−7.48 pp**
- exact McNemar p = **0.00940**

P5R vs P5:
- P5-only: 17
- P5R-only: 26
- accuracy delta: **+3.54 pp**
- exact McNemar p = **0.222**

The holdout therefore confirms the direction of the P5R vs P0 degradation and does not provide evidence of a robust P5R advantage over P5.

## 4. Gate A — deterministic evidence-only termination

P5R non-escalated cases terminate after deterministic evidence without an LLM call.

Development:
- n = 352
- P5R official correctness = **0/352 (0%)**
- P0 correctness within the same cases = **89/352 (25.28%)**
- 89/254 P0-correct cases are therefore lost by the current non-escalation decision.

Holdout:
- n = 108
- P5R official correctness = **0/108 (0%)**
- P0 correctness within the same cases = **33/108 (30.56%)**
- 33/60 P0-correct holdout cases are therefore lost by the current non-escalation decision.

The frozen P1 deterministic-only baseline also has 0 official-correct cases on the full 1,034-case workload.

### Gate A decision: FAIL for the current implementation

The evidence supports the narrow conclusion that **the current deterministic evidence result cannot be accepted as the final analytical answer**. It may still be useful as an intermediate feature or candidate generator.

This does not establish that all deterministic evidence is intrinsically useless; it establishes that this implementation cannot serve as a correctness-preserving terminal action.

## 5. Gate B — evidence-state predictive signal

A diagnostic model was fit using only label-free P5R post-evidence features, with frozen P0 official correctness as the downstream-success target. The model was not used to modify P5R and was not used to tune the holdout.

Using `reason + evidence_row_count + evidence_column_count`:

Development, 5-fold stratified cross-validation:
- ROC-AUC = **0.696**
- average precision = **0.388**
- Brier score = **0.218**

Fit on the 780-case development partition and evaluated once on the untouched 254-case holdout:
- ROC-AUC = **0.791**
- bootstrap 95% CI = **[0.731, 0.846]**
- average precision = **0.510**
- Brier score = **0.191**

Adding execution/generation status and the escalation flag produced development cross-validation ROC-AUC **0.717**, but the simpler evidence-state model is preferred for interpretation because it more directly tests the post-evidence information content.

### Gate B decision: PASS as a diagnostic signal, not as a deployable selector

The result indicates that post-evidence state is not information-free. However, predictive ranking is not a reliability guarantee, and the current hand-built selector is not calibrated to the research reliability targets.

## 6. Selector preservation failure

Development P5R:
- non-escalation: 352 cases, 0 P5R-correct, 89 P0-correct;
- escalation: 682 cases, 179 P5R-correct, 165 P0-correct.

Among P5R escalations, the challenger can rescue cases that P0 misses, but it can also replace a correct incumbent with an incorrect challenger. Overall P5R has 37 rescues of P0 failures and 112 losses of P0 successes.

The clean P5R evidence therefore supports a more precise mechanism diagnosis than the original frozen P5 result: **the problem is not simply absence of signal; it is failure to translate the signal into a correctness-preserving action policy.**

## 7. Evidence-reason heterogeneity

Development P0 correctness by P5R evidence reason:

| Reason | n | P0 correctness |
|---|---:|---:|
| requested_name_not_projected | 172 | 26.74% |
| question_predicate_not_reflected | 160 | 23.13% |
| extremum_not_reflected | 102 | 16.67% |
| grouping_not_reflected | 91 | 10.99% |
| aggregation_not_reflected | 65 | 15.38% |
| literal_predicate_not_reflected | 62 | 46.77% |
| ordering_not_reflected | 30 | 53.33% |

Reason category is associated with P0 correctness on development data (chi-square p = **2.48e-08**). The category rates shift substantially on holdout, so the categories should not be treated as calibrated probabilities.

## 8. What this means for the original research question

The original research question remains unchanged: whether evidence-dependent analytical action selection can select a lower-cost sufficient action while satisfying a predefined reliability target, outperforming fixed strategies and strong post-evidence cascade baselines.

The current evidence now supports this mechanism tree:

- **P5 is cheaper than P0 but much less reliable.**
- **P5R improves P5 accuracy, indicating that selector/mechanism design contributes to the failure.**
- **P5R still loses to P0 and is more expensive than P0, so the broader evidence-dependent hypothesis is not yet supported.**
- **The current deterministic terminal action fails Gate A.**
- **Post-evidence features pass a limited diagnostic information test (Gate B), but the current selector does not provide reliability preservation.**

## 9. P6 gate remains blocked

No P6 claim is made from P5R.

A future P6 is justified only if a policy is first specified and frozen on the 16-schema development partition, with no use of holdout outcomes, and then prospectively evaluated on the four held-out schemas.

Any such policy must predeclare:

- the action-selection rule;
- the acceptance/replacement rule;
- the reliability target and confidence interval criterion;
- cost accounting;
- timeout/error treatment;
- preservation and rescue metrics;
- ablations that distinguish evidence value from selector value.

If these conditions do not yield a defensible reliability-constrained advantage, the correct research contribution is an empirical boundary/failure-mode result rather than a forced positive routing claim.
