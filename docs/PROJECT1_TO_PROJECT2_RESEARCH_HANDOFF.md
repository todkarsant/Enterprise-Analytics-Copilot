# Project 1 → Project 2 Research Handoff

**Project 1:** Enterprise Analytics Copilot  
**Project 2:** Production LLM Evaluation & Observability Platform  
**Status:** Project 1 algorithmic development stopped; research transfer specification established.  
**Date:** 2026-09-09

## 1. Why this handoff exists

Project 1 was initially framed around cost-aware, evidence-dependent analytical execution. The final controlled challenger (P6-IP) showed that intermediate evidence plus basic executable/structural verification was not sufficient to safely replace a potentially correct incumbent.

This does not create an unrelated new problem. It exposes a latent problem that aggregate accuracy and routing studies can hide:

> **Evidence that is predictive of correctness is not automatically sufficient evidence for consequential action.**

The next repository must therefore study measurement, attribution, observability, and control of this gap rather than immediately invent another routing heuristic.

## 2. Locked Project 1 finding

On development (1,034 cases):

- P0 accuracy: 24.565%
- P6-IP accuracy: 22.631%
- paired difference: -1.934 pp
- intervention-eligible: 330
- harm: 21/62 = 33.87% of P0-correct eligible cases
- rescue: 2/268 = 0.75% of P0-wrong eligible cases
- mean cost: +25.8% versus P0
- exact McNemar p = 0.001193

Held-out schemas (254 cases) show the same direction: 31.25% harm versus 1.33% rescue among eligible cases and +29.2% mean cost. Because the historical P6 workflow executed holdout cases before full development aggregation/freeze, holdout is locked observational corroboration rather than a fully prospective confirmatory run.

The Project 1 stop rule therefore failed and algorithm development is stopped.

## 3. Scientific problem decomposition

Project 1 established three different questions:

1. **Prediction:** Does evidence predict whether an incumbent answer is correct?
2. **Intervention:** Is the expected value of additional computation high enough to justify spending more resources?
3. **Replacement:** Is the evidence strong enough to authorize replacing the incumbent?

Project 1 found diagnostic evidence of prediction signal, but P6-IP failed at the replacement decision.

Project 2 must preserve this decomposition.

## 4. Project 2 research question

> **Can an evaluation and observability layer detect, attribute, and continuously monitor the gap between evidence that predicts analytical correctness and evidence that is safe to use for consequential agent actions?**

This is deliberately different from:

- "Can we build a better router?"
- "Can we make an LLM more accurate?"
- "Can we add another confidence score?"

## 5. Project 2 hypotheses

### H2.1 — Prediction/action separation
Correctness-predictive signals will not necessarily have sufficient precision or calibration for action authorization under asymmetric harm costs.

### H2.2 — Decision observability
Case-level provenance and decision traces will reveal failure modes that aggregate accuracy, cost, or confidence metrics conceal.

### H2.3 — Verification gap
Executable/structurally valid outputs will remain an incomplete proxy for semantic correctness unless stronger verification evidence is available.

### H2.4 — Drift
The relationship between evidence signals and safe action will vary across schemas, models, policies, and time; monitoring only aggregate accuracy will miss such drift.

### H2.5 — Defensibility
Separating decision-time evidence from post-hoc evaluator labels makes experiments more reproducible and prevents oracle leakage in evaluation/control logic.

## 6. Required capabilities inherited from Project 1

Project 2 should implement these as measurable primitives, not dashboard decoration:

1. evaluator integrity and denominator validation;
2. dataset/split lineage and freeze-state enforcement;
3. case-level decision provenance;
4. decision-time versus post-hoc field separation;
5. incumbent/challenger paired evaluation;
6. harm/rescue/preserved-correct/preserved-wrong outcome classes;
7. verification coverage and verification-failure taxonomy;
8. semantic-correctness versus executability gap metrics;
9. cost per case and cost per rescue/harm event;
10. P50/P95/P99 latency and timeout observability;
11. policy/model/provider/version lineage;
12. intervention and replacement-rate monitoring;
13. correctness, harm, rescue, and verification drift;
14. reproducible experiment state machine;
15. auditable machine-readable decision records.

## 7. Required Project 2 data model

Every evaluated decision should be reconstructable from a record containing, at minimum:

- case ID and dataset/split;
- schema/domain identifier;
- model/provider/version;
- policy/version/commit;
- tools/actions available;
- evidence produced before the decision;
- evidence provenance;
- decision and decision reason;
- verification checks and results;
- authorization/control metadata when available;
- incumbent output;
- challenger/output candidate when applicable;
- final selected output;
- post-hoc official correctness;
- harm/rescue/preservation class;
- cost/tokens/calls;
- latency/tail-latency information;
- runtime/timeout/error state;
- timestamp/correlation ID;
- reproducibility manifest.

Gold/evaluator fields must be explicitly marked post hoc and must never be available to the decision policy during inference.

## 8. Project 2 evaluation model

The next project should report at least four separate axes:

```text
CORRECTNESS
    ├── execution accuracy
    ├── semantic correctness
    └── selective prediction metrics

ACTION SAFETY
    ├── intervention precision
    ├── harm rate
    ├── rescue rate
    └── replacement acceptance quality

EFFICIENCY
    ├── cost
    ├── model calls/tokens
    └── P50/P95/P99 latency

DEFENSIBILITY / OBSERVABILITY
    ├── provenance completeness
    ├── verification coverage
    ├── evaluator integrity
    ├── policy/model lineage
    └── reproducibility
```

These axes must not be collapsed into one arbitrary score.

## 9. Research contribution expected from Project 2

The strongest continuation is a methodology for **decision-aware LLM evaluation and observability** in which the evaluation system can distinguish:

- a model that is inaccurate;
- a model that is uncertain;
- an evidence signal that is predictive;
- a policy that spends more computation appropriately;
- a policy that intervenes but causes harm;
- a verifier that filters invalid outputs but cannot establish semantic correctness;
- a system whose aggregate metrics look stable while harm/rescue behavior drifts.

This would convert Project 1's empirical failure boundary into a general measurement problem without claiming universal safety.

## 10. What must NOT be inherited

Project 2 must not inherit these assumptions:

- that P6-IP should be improved until it wins;
- that another routing heuristic is automatically the next contribution;
- that a confidence score is an authorization mechanism;
- that executable SQL is equivalent to correct SQL;
- that aggregate accuracy is sufficient for decision safety;
- that Spider alone proves enterprise production readiness;
- that the Project 1 holdout was fully prospective;
- that Project 1 established a universal impossibility result.

## 11. Paper-to-paper continuity

### Project 1 paper
**When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents**

Core finding:

> Intermediate evidence can justify investigation without being sufficient to authorize incumbent replacement.

### Project 2 paper — proposed direction
**From Evaluation to Defensibility: Observability of Reliability-Critical LLM Decisions**

Core question:

> Can we measure and monitor the gap between predictive evidence, actionable evidence, and evidence sufficient for consequential action?

The Project 2 paper should cite Project 1 as the empirical motivation for the evaluation/observability problem, not as proof of a universal limitation.

## 12. Portfolio progression

```text
PROJECT 1 — Enterprise Analytics Copilot

Can an analytical agent use intermediate evidence to act more efficiently and safely?
                    ↓
            NEGATIVE BOUNDARY
 evidence ≠ safe replacement authorization
                    ↓
PROJECT 2 — Evaluation & Observability

Can we measure, attribute, and monitor that boundary?
                    ↓
PROJECT 3 — AI Marketing Spend Optimizer

Can consequential business optimization operate under those measured
reliability, uncertainty, cost, provenance, and action-risk constraints?
```

The projects therefore form a single research progression rather than three disconnected portfolio applications.

## 13. Transfer artifacts

Project 2 must receive the following locked Project 1 artifacts:

- `paper/PROJECT1_PAPER_DRAFT.md`
- `docs/PROJECT1_P6_IP_RESULTS.md`
- `docs/PROJECT1_DEFENSIBILITY_LAYER.md`
- `docs/PROJECT1_P6_IP_EXECUTION_HANDOFF.md`
- P0–P5 frozen benchmark manifest and artifacts
- P6-IP decision records
- official evaluator commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- P6 controlled run `34252265013`
- corrected analysis run `34283127475`
- research state/stop-rule evidence

The transfer should be versioned and immutable before Project 2 begins scientific experimentation.

## 14. Definition of done for Project 1 before Project 2 consumes the result

Project 1 is scientifically closed when:

- P0–P5 remain frozen;
- P6-IP stop decision is recorded;
- corrected comparator analysis is locked;
- decision-record integrity is tested;
- holdout protocol deviation is disclosed;
- paper draft contains the negative result and limitations;
- Project 1 → Project 2 handoff is versioned;
- no further P6/P7/P8 inference is launched merely to improve the result.

**The purpose of Project 2 is therefore not to rescue Project 1's algorithm. It is to turn Project 1's failure boundary into a measurable, reproducible, and monitorable research object.**
