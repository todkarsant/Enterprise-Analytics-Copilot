# P5 Mechanism Forensic Result — Frozen Evidence

Date: 2026-09-08  
Source run: `34206500727`  
Model/provider: `llama3.2:1b` / local Ollama  
Status: diagnostic result; no new inference

## 1. Primary conclusion

The frozen evidence is consistent with a **routing/selector failure interacting with a weak deterministic baseline**, not evidence that post-evidence escalation is intrinsically useful.

P5 is substantially below P0 on official Spider execution correctness. The mechanism analysis therefore does not justify implementing P6 as a performance-recovery step.

## 2. Paired P0/P5 evidence

Full 1,034 cases:
- P0 correct: 254
- P5 correct: 123
- P0-only: 158
- P5-only: 27
- P5 − P0: −12.67 percentage points

The frozen review reports an exact paired McNemar result on the discordant pairs at approximately p = 1e-23, strongly rejecting the hypothesis that the observed P0/P5 disagreement is symmetric.

Schema-disjoint partition:
- 780 cases across 16 non-holdout schemas: P0 193/780 (24.74%), P5 91/780 (11.67%).
- 254 cases across four held-out schemas: P0 60/254 (23.62%), P5 32/254 (12.60%).

The holdout result must be interpreted conditionally on the fact that the four schemas were also present in the full 1,034-case artifact. The defensible split is 16 schemas development / 4 schemas holdout, provided those holdout schemas were not used for policy tuning.

## 3. Escalation selector signal

P5 has 541 escalated cases and 493 non-escalated cases.

The 493 non-escalated cases contain **zero P5 official-correct cases**. P0 nevertheless has 142 correct cases within this same group. Therefore the observed non-escalation decision is not a sufficient correctness proxy.

Among escalated cases, P5 has 123 correct cases. Relative to P0 on those cases:
- both correct: 96
- P5 rescue of P0 failure: 27
- P5 destruction of P0 success: 16

Thus escalation provides some rescue, but its gross benefit is overwhelmed by P5 failures elsewhere and by a lack of preservation guarantees.

## 4. Deterministic baseline limitation

The deterministic solver is explicitly described as conservative and limited to direct/single-table aggregate/order patterns. This means P5's first-stage behavior is not a general SQL reasoner. P5 can therefore inherit deterministic failures before its heuristic evidence trigger has a chance to identify the relevant semantic defect.

This is a key confounder: a poor deterministic baseline can make evidence-trigger design look worse than the routing concept itself. The current evidence does not permit the stronger causal claim that evidence-based routing is fundamentally invalid.

## 5. Selector design limitation

`needs_post_evidence_escalation()` relies on lexical structural cues, result cardinality, and checks for whether generated SQL contains constructs such as WHERE/JOIN/GROUP BY/ORDER BY. It is a hand-built heuristic rather than a calibrated probability of downstream correction.

The P4 confidence value is also heuristic rather than empirically calibrated, and P2/P3 share the same complexity threshold in the current implementation. These facts limit the strength of any claim that the experiment compared distinct, independently calibrated routing policies.

## 6. Preservation failure

P5 overwrites the deterministic SQL with the escalated SQL whenever escalation occurs. The frozen implementation has no general 'preserve incumbent if confidence/evidence does not establish improvement' gate. The paired outcomes show 16 P0 successes becoming P5 failures among escalated cases.

This is an actionable mechanism hypothesis for prospective work: **escalation should be challenger generation, not unconditional replacement**.

## 7. What can and cannot be claimed

Supported:
- P5 is substantially worse than P0 on the frozen workload.
- P5 saves measured cost and average LLM usage relative to P0.
- The selector misses many cases where downstream LLM generation could be relevant.
- Escalation can rescue some P0 failures but can also destroy correct deterministic outputs.
- Deterministic-solver scope and selector heuristics are major experimental limitations.

Not supported:
- That a better selector would achieve 90% reliability.
- That a preservation gate would improve accuracy, because no prospective generation has been performed for the altered policy.
- That the failure proves all evidence-based routing is invalid.
- That the four-schema holdout is an untouched independent test if its schemas were used during development/tuning.

## 8. Implementation gate

A prospective P6 is permitted only if it is first specified and frozen on the 16-schema development partition, with no use of holdout outcomes. The candidate should treat deterministic SQL as an incumbent and LLM output as a challenger, and require an explicit acceptance rule before replacement.

The acceptance rule must be evaluated prospectively on held-out schemas; counterfactual replay of frozen outputs is diagnostic only and cannot establish correctness of newly generated SQL.
