# AI Auditing / Accountability Integration for Project 1

**Reference:** Birhane, A., Steed, R., Ojewale, V., Vecchione, B., & Raji, I. D. (2024). *AI auditing: The Broken Bus on the Road to AI Accountability*. arXiv:2401.14462. https://arxiv.org/abs/2401.14462

## Role in Project 1

This work should be treated as a **research-framing and auditability reference**, not as a new experimental method and not as evidence for Project 1's empirical results. The paper argues that meaningful AI accountability depends not simply on performing an audit, but on how audit design, methodology, stakeholders, and institutional context affect whether audit findings translate into accountability outcomes.

Project 1 can use this perspective to sharpen its distinction between **evaluation**, **auditability**, and **accountability**.

## Integration into the Project 1 argument

Project 1 already separates three decision levels:

1. **Prediction:** is the incumbent likely to be wrong?
2. **Intervention:** is additional computation justified?
3. **Authorization:** is the evidence strong enough to replace the incumbent?

The AI-auditing literature provides a complementary fourth question:

4. **Accountability:** can the consequential decision be reconstructed, challenged, and evaluated from preserved evidence and provenance?

This yields the following conceptual chain:

```text
prediction
    ↓
intervention
    ↓
replacement authorization
    ↓
accountability / auditability
```

The fourth level is **not** being introduced as a new benchmark metric. It is a framing layer for interpreting the Defensibility Layer already present in Project 1.

## Defensibility Layer interpretation

The existing Defensibility Layer records:

- decision-time evidence;
- evidence provenance;
- policy rationale;
- verification results;
- authorization hooks;
- outcome;
- cost and latency;
- reproducibility information.

In light of Birhane et al., these records should be described as mechanisms that make an analytical-agent decision **auditable and contestable**, rather than as proof that the system is accountable or compliant. The distinction is important: logging an action is not equivalent to demonstrating that an organization has acted on audit findings or established effective accountability.

## What this strengthens

### 1. Evaluation versus audit

Official Spider execution accuracy answers a correctness question under a controlled benchmark. It does not by itself establish that the agent's consequential decisions are reconstructable or governable. Project 1 can therefore explicitly distinguish:

```text
Benchmark evaluation
    = Did the system produce the correct SQL/result?

AI auditability
    = Can we reconstruct why and how the system acted?

Accountability
    = Can the resulting evidence support challenge, remediation,
      ownership and consequential oversight?
```

### 2. Failure analysis

The existing harm/rescue analysis becomes more than a performance table. It identifies a consequential asymmetry: an intervention can be triggered by evidence that is useful for risk detection while still being unsafe as replacement authority. The auditability framing supports preserving the decision trace needed to inspect such failures without using post-hoc correctness as a decision-time signal.

### 3. Provenance and reproducibility

The pinned official evaluator, frozen benchmark partitions, raw traces, correction manifests, and separation between decision-time evidence and post-hoc labels should be presented as **evidence-provenance controls**. They improve reproducibility and auditability; they should not be described as establishing universal accountability.

### 4. Institutional-context boundary

Spider cannot establish production accountability, access-control correctness, organizational ownership, regulatory compliance, or human oversight. The paper should therefore avoid implying that a benchmark audit is equivalent to an enterprise AI audit. This reinforces the existing limitation that Project 1 is an empirical mechanism-boundary study rather than a production-governance claim.

## Suggested manuscript language

The following paragraph can be incorporated into the literature/threat-model or Defensibility Layer discussion:

> **AI auditing and accountability.** Recent work on AI auditing cautions that an audit is not automatically an accountability mechanism: the effectiveness of an audit depends on its design, methodology, stakeholders, and institutional context [31]. This distinction is relevant to analytical agents because benchmark correctness and post-hoc evaluation do not by themselves make a consequential decision reconstructable or contestable. Project 1 therefore treats auditability as a separate evidence layer. Decision-time evidence, provenance, policy rationale, verification outcomes, authorization hooks, and reproducibility records are preserved separately from post-hoc correctness labels. These controls support reconstruction and evaluation of consequential agent decisions; they are not claimed to establish legal compliance, organizational accountability, or production readiness.

## Suggested addition to the research contribution

Do **not** claim that Project 1 invents AI auditing. Instead, the defensible contribution is narrower:

> Project 1 operationalizes an auditability-oriented evidence record around the experimentally tested distinction between correctness prediction, intervention eligibility, and replacement authorization, then uses paired harm/rescue outcomes to expose a reliability boundary.

This should be presented as a **connection to the AI-auditing literature**, not as a new audit framework unless a future study formally evaluates that framework.

## Reviewer-risk guardrails

A strict reviewer could object if the paper:

- equates benchmark evaluation with an AI audit;
- claims that provenance logs prove accountability;
- claims regulatory or legal compliance from Spider results;
- presents the auditability layer as novel without a comparative audit study;
- uses Birhane et al. as evidence that P6-IP fails;
- changes the benchmark, evaluator, scoring, or P6 stop rule because of this literature.

Those claims should remain explicitly out of scope.

## Methodology lock

This integration is **literature/framing only**. It does not modify:

- the 1,034-case Spider benchmark;
- the 254-case unseen-schema holdout;
- the pinned official Spider evaluator;
- the local Ollama inference requirement;
- reliability thresholds;
- statistical tests;
- P5/P6 stop rules;
- model prompts or scores.

No new experiment is implied by this literature integration.