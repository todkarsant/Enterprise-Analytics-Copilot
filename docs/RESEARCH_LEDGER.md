# Research Ledger

This ledger links eventual claims to experiments and evidence. Entries are intentionally created before results exist.

| Claim ID | Planned claim | Evidence required | Status |
|---|---|---|---|
| CLAIM-001 | P6 improves the reliability-constrained cost frontier over P5, if and only if matched-reliability cost is lower on held-out data. | EXP-001, EXP-002 | Pending |
| CLAIM-002 | Any P6 gain persists on unseen schemas. | EXP-003 | Pending |
| CLAIM-003 | P6's gain is attributable to heterogeneous action selection rather than additional compute alone. | EXP-004 ablations | Pending |
| CLAIM-004 | Reliability gains are not explained by abstention/coverage reduction. | EXP-005 coverage analysis | Pending |
| CLAIM-005 | Policy overhead is included in reported efficiency. | EXP-006 accounting audit | Pending |
| CLAIM-006 | Reliability failures differ by workload stratum and require different interventions. | EXP-007 failure taxonomy | Pending |
| CLAIM-007 | Results are robust to stochastic variation and threshold choices. | EXP-008 repeated runs/sensitivity | Pending |

## Planned experiments

### EXP-001 — Baseline frontier

Run P0-P5 on the frozen benchmark and establish reliability/cost/latency frontiers.

### EXP-002 — Primary P5 vs P6

Run P5 and P6 with matched models, data, environment and budgets.

### EXP-003 — Unseen-schema transfer

Evaluate frozen policies on schemas not used for tuning.

### EXP-004 — Mechanism ablations

Remove heterogeneous action classes and evidence features to determine the source of gains.

### EXP-005 — Coverage audit

Report correctness, abstention, clarification and coverage jointly.

### EXP-006 — Cost accounting audit

Verify that router/verifier/retrieval/repair/escalation costs are included.

### EXP-007 — Failure taxonomy

Analyze errors by semantic, structural, governance, ambiguity and execution categories.

### EXP-008 — Robustness

Repeat stochastic policies and evaluate threshold/budget sensitivity using frozen test data only for final reporting.

## Claim rule

A claim remains `Pending` until the corresponding experiment is complete and independently checked. A negative result must be recorded rather than removed from the ledger.
