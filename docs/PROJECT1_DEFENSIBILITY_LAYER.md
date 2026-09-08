# Project 1 — Defensibility Layer

**Status:** Approved research-design layer. It is separate from P6-IP and does not change the frozen benchmark or the primary scientific question.

## 1. Purpose

The Defensibility Layer operationalizes enterprise AI defensibility around the analytical decision itself. It does not turn Project 1 into a generic governance framework and does not rely on a vendor-specific definition.

The layer answers five audit questions for every analytical decision:

1. **What did the agent decide?**
2. **What evidence did it use?**
3. **Which policy/risk rule caused the action?**
4. **What verification and authorization controls were applied?**
5. **What outcome, cost, and accountability evidence was recorded?**

The research architecture therefore becomes:

```text
question
   ↓
analytical execution
   ↓
evidence
   ↓
policy / risk decision
   ↓
verification + authorization
   ↓
outcome
   ↓
Defensibility Layer
   ├── provenance
   ├── decision rationale
   ├── control evidence
   ├── outcome + intervention audit
   ├── cost / latency / reliability
   └── reproducible trace
```

## 2. Scope boundary

The Defensibility Layer is an **observability and control-evidence layer**, not a claim that the system is fully production-governed.

It must not be used to retroactively change benchmark decisions, labels, exclusions, or metrics.

P0–P5 evidence remains frozen. P5R remains a challenger. P6-IP remains the final controlled reliability experiment.

## 3. Decision record contract

Every P6-IP decision should expose, where available:

- `case_id` / stable question identifier;
- database/schema identifier;
- policy version and code commit;
- model/provider and model version;
- dataset/evaluator manifest;
- incumbent action and incumbent answer/SQL;
- evidence observed before intervention;
- evidence provenance (which tool/action produced it);
- risk/selector reason;
- intervention decision: KEEP / INTERVENE;
- challenger answer/SQL;
- verification checks and their results;
- replacement decision: ACCEPT / REJECT / PRESERVE;
- final outcome;
- intervention class: rescue / harm / preserved-correct / preserved-wrong;
- abstention/clarification/runtime outcome;
- latency, token counts, LLM calls and research cost;
- timeout/error information;
- timestamp and trace correlation identifier.

Gold labels and evaluator outcomes may be stored for **post-hoc evaluation**, but must be explicitly separated from decision-time fields so that no oracle leakage is possible.

## 4. Defensibility metrics

### A. Decision trace completeness

Measure the fraction of decisions containing all required decision-time fields.

`trace_completeness = complete_decision_records / evaluated_decisions`

Missing trace fields are reported as observability failures, not silently imputed.

### B. Evidence provenance completeness

For every intervention, record which evidence source and action produced the trigger. Provenance must be reconstructable from the raw trace.

### C. Policy explainability

Every intervention/retention decision must have a machine-readable reason code. Free-form explanations are supplemental, not the authoritative audit field.

### D. Verification coverage

Report the fraction of replacements for which every required verification gate executed successfully.

### E. Incumbent harm / rescue

Report harm and rescue separately. A lower error rate caused by suppressing interventions is not equivalent to successful intelligence.

### F. Authorization correctness

Where enterprise authorization metadata is available, record whether the requested action was permitted under the applicable policy. Authorization failures remain distinct from analytical correctness.

### G. Reliability and cost

Continue to report official Spider execution accuracy, Wilson confidence intervals, paired effects, latency, token use, tool calls, coverage, and timeout/error rates. Defensibility does not replace correctness.

### H. Audit reproducibility

A decision should be replayable from its recorded dataset/evaluator/model/policy manifests and trace artifacts, subject to nondeterminism limits of the underlying model.

## 5. Governance/control hooks

The research implementation should expose explicit hook points for:

```text
authorization check
       ↓
data-access policy
       ↓
tool/action allow-list
       ↓
SQL safety validation
       ↓
execution budget / timeout
       ↓
verification
       ↓
auditable outcome
```

For the Spider experiment, authorization may be represented as a **control interface/fixture** rather than real enterprise identity data. The benchmark must not invent business permissions that are not part of the dataset.

Future enterprise evaluation can plug in RBAC/ABAC policies and measure authorization correctness separately from SQL correctness.

## 6. Runtime reliability hooks

The layer should make the following observable without changing the research denominator:

- timeout and runtime-error events;
- policy version drift;
- model/provider changes;
- token/cost drift;
- latency distributions and tail latency;
- correctness drift across schema families;
- intervention/harm/rescue drift;
- verification rejection rates;
- abstention and clarification rates.

These are monitoring hooks, not evidence of production readiness by themselves.

## 7. Research hypotheses enabled by the layer

**H-D1 — Evidence traceability:** complete provenance and decision records can identify why a policy intervened or preserved an incumbent.

**H-D2 — Reliability accountability:** incumbent harm is measurable as a first-class operational failure rather than being hidden inside aggregate accuracy.

**H-D3 — Control observability:** verification, authorization, timeout, and budget controls can be evaluated independently of model capability.

**H-D4 — Generalization:** defensibility metrics remain meaningful across unseen schemas and model/provider changes without redefining correctness.

These hypotheses are secondary to the core P6-IP reliability experiment unless explicitly promoted in the final paper.

## 8. Reporting rule

The final paper/white paper should distinguish three layers of evidence:

1. **Scientific evidence:** accuracy, cost, latency, paired statistics, confidence intervals, generalization, ablations.
2. **Decision evidence:** evidence provenance, policy reasons, verification results, intervention/rescue/harm.
3. **Governance evidence:** authorization/control hooks, trace completeness, monitoring readiness, accountability fields.

A system can be statistically well evaluated but operationally weakly defensible, or operationally observable but statistically unreliable. Do not collapse these into one score.

## 9. Defensibility boundary

The layer supports a defensible engineering posture by making decisions, evidence, controls, and outcomes auditable. It does **not** prove legal compliance, enterprise governance completeness, explainability in a human-factors sense, or production readiness.

Those claims require separate evidence and should not be inferred from the Spider experiment.
