# When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents

**Project:** Project 1 — Enterprise Analytics Copilot  
**Status:** Living paper draft; empirical results are locked to the executed evidence.  
**Repository branch:** `research/p6-ip-defensibility`  
**Last updated:** 2026-09-09

> **Scientific positioning.** This paper is an empirical boundary/failure-mode study. It does not claim that adaptive routing, cascades, verification, selective prediction, Text-to-SQL, or governance metadata are individually novel. The narrower claim is that, under the tested cross-schema analytical setting, decision-time evidence combined with low-cost executable/structural verification was not sufficient to authorize safe incumbent replacement. The paper therefore separates **correctness prediction**, **intervention**, and **replacement authorization** rather than treating them as one problem.

---

## Abstract

LLM-based analytical agents must balance correctness, computational cost, latency, and operational accountability. A natural strategy is to use intermediate evidence generated during execution to decide whether to spend additional computation or replace an incumbent analytical answer. However, evidence that is informative for identifying risk need not be sufficiently reliable to authorize replacement of an answer that may already be correct.

We study this distinction in an evidence-dependent analytical execution framework evaluated on the Spider benchmark under a frozen cross-schema protocol. The study first establishes fixed, query-only, heuristic-confidence, and post-evidence cascade baselines (P0–P5). It then evaluates an incumbent-preserving challenger (P6-IP) that begins from a P0 incumbent, uses only decision-time evidence to determine intervention eligibility, generates a challenger for eligible cases, and replaces the incumbent only after predefined SQL validity, execution, and structural checks. The primary outcome is official Spider execution accuracy, complemented by paired harm/rescue analysis, cost, latency, statistical comparison, and decision-trace integrity.

On the 1,034-case development evaluation, P0 obtains 254 correct cases (24.565%) versus 234 (22.631%) for P6-IP, a paired difference of -1.934 percentage points (exact McNemar p=0.001193). Among intervention-eligible cases, 33.87% of P0-correct cases are harmed while only 0.75% of P0-wrong cases are rescued. Mean P6-IP cost is 25.8% higher than P0. The held-out-schema partition shows the same direction, with 31.25% harm versus 1.33% rescue among eligible cases and 29.2% higher mean cost. The historical holdout execution occurred before complete development aggregation/freeze; it is therefore treated as locked observational corroboration rather than a fully prospective confirmatory test.

The results do not establish that evidence-dependent intervention or verification is impossible. They establish a narrower mechanism boundary: the tested evidence class, challenger generation process, and basic verification gate were not reliable enough for asymmetric incumbent replacement. This supports a methodological distinction between **evidence sufficient to investigate** and **evidence sufficient to authorize consequential action**. The paper then connects this boundary to an explicit Defensibility Layer based on provenance, policy rationale, verification, authorization hooks, outcome, cost, latency, and reproducibility. Gartner's 2026 work on Defensible AI, AI-agent reliability, trust engineering, and LLM observability is used as industry-context evidence for why these controls matter; it is not used as evidence of academic novelty.

---

## 1. Introduction

LLM-based analytical agents increasingly combine schema retrieval, retrieval of examples, SQL generation, execution, verification, repair, clarification, and escalation. This creates a sequential decision problem: after each step, the system has accumulated evidence and must choose the next action. A tempting objective is to minimize computational cost subject to a reliability target.

The supplied literature corpus shows that this general idea is already well populated. Research has studied adaptive tool use, model routing, cascades, post-retrieval escalation, semantic SQL execution, selective prediction, correctness estimation, abstention, reference-free SQL verification, and enterprise governance. The paper therefore does **not** ask whether an agent can route or cascade. Those mechanisms are established research directions.

The narrower problem is asymmetric action authorization.

> **When an analytical agent obtains intermediate evidence suggesting that its incumbent answer may be incorrect, what evidence is sufficient to justify additional computation, and what evidence is sufficient to justify replacing the incumbent without unacceptable reliability loss?**

This distinction matters because the errors are asymmetric. Spending additional computation on an incumbent that was already correct is primarily a cost error. Replacing a correct incumbent with an incorrect challenger is a reliability error. Consequently, a signal can be useful as a **risk detector** while being unsafe as a **replacement authority**.

This distinction is also consistent with current industry reliability thinking. Gartner's 2026 research frames enterprise AI-agent reliability as a system-level problem involving scope, autonomy, guardrails, monitoring, and demonstrated reliability rather than model capability alone. Gartner separately describes Defensible AI and AgentOps as emerging enterprise architecture responsibilities and identifies explainability and LLM observability as trust layers for scaling GenAI. These sources motivate the engineering relevance of the problem, but they do not establish the academic gap claimed here.

Project 1 was deliberately designed as a falsification-oriented sequence rather than an optimization exercise:

1. freeze strong policy baselines;
2. test whether post-evidence escalation actually improves the reliability-cost frontier;
3. inspect the mechanism rather than immediately invent another router;
4. test a stricter forensic evidence selector;
5. introduce incumbent preservation and a predefined replacement gate;
6. evaluate harm and rescue explicitly;
7. stop algorithm development if the challenger cannot materially improve the asymmetric trade-off.

The final result is negative for P6-IP. That negative result is scientifically useful because it exposes a decision boundary that aggregate accuracy and routing literature can obscure.

### Contributions

The paper makes five deliberately bounded contributions:

1. **Decision decomposition.** It separates three decisions that are often conflated: correctness prediction, intervention eligibility, and incumbent replacement authorization.
2. **Incumbent-aware evaluation.** It evaluates intervention using paired harm/rescue outcomes in addition to aggregate accuracy.
3. **Mechanism-boundary evidence.** It shows that executable and structurally valid challenger SQL was insufficient for safe incumbent replacement under the tested conditions.
4. **Reproducible experimental discipline.** It uses a frozen evaluator, fixed schema partitioning, isolated execution, explicit denominator checks, paired statistical tests, and post-hoc evaluator-integrity repair without rerunning LLM inference.
5. **Defensibility-oriented decision evidence.** It records decision-time evidence and provenance separately from post-hoc gold/evaluator labels, creating a concrete bridge to evaluation and observability research.

The paper explicitly does **not** claim universal optimality, a general impossibility theorem, generic routing novelty, production governance compliance, or production enterprise readiness.

---

## 2. Literature Positioning and the Actual Gap

### 2.1 What the supplied literature already covers

The literature review was treated as a threat model for novelty rather than a collection of supportive citations. The supplied corpus contains multiple overlapping families:

| Literature family | What is already established | Why it constrains this paper |
|---|---|---|
| Adaptive routing / cascades | Systems can defer expensive computation, route requests, or cascade from cheap to expensive actions. | Project 1 cannot claim routing itself as novel. |
| Post-evidence escalation | Some tasks reveal the need for more computation only after retrieval/execution evidence is observed. | Supports the use of decision-time evidence, but not replacement safety. |
| Semantic SQL cascades / online learning | Execution-time policies can optimize LLM-related query cost. | A direct novelty threat to generic cost-aware analytical routing. |
| Selective prediction | Correctness can be estimated and systems can abstain or selectively answer. | Distinguishes correctness estimation from consequential action authorization. |
| SQL verification | Executability, structural consistency, learned verifiers, and LLM judges can estimate SQL correctness. | Shows that verification is itself a substantial research area; the paper must not claim it invented verification. |
| Abstention / human-in-the-loop | Systems can defer difficult or ambiguous cases rather than answer automatically. | Demonstrates a safer alternative to automatic replacement. |
| Interactive Text-to-SQL | Ambiguity and unanswerability can require clarification and interaction. | Shows that evidence may indicate uncertainty without uniquely determining a safe answer. |
| Enterprise semantic governance | Governed metrics, joins, filters, security, and cost rules can constrain analytical SQL. | Shows that enterprise safety is broader than SQL execution correctness. |

Representative directly constraining works include *What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study* (arXiv:2607.06799), *Compositional Online Learning for Semantic Data Processing Systems* (arXiv:2608.27244), *Reliable Text-to-SQL with Adaptive Abstention* (arXiv:2501.10858), *The Coverage Illusion* (arXiv:2605.27220), *TraceSQL* (arXiv:2608.17795), *ABISS* (arXiv:2607.23340), and *GROUND* (arXiv:2608.26157). These are not presented as an exhaustive bibliography of the supplied corpus; they are the most directly constraining examples for the claims made here.

### 2.2 The gap is not “adaptive routing”

A reviewer should therefore not read the paper as claiming:

> “Prior work did not adapt execution, so we introduced adaptive execution.”

That claim would be false.

The gap is narrower and operationally testable:

> **Prior work commonly asks whether evidence can predict correctness, whether additional computation is worthwhile, or whether a candidate can be verified. Project 1 asks whether that evidence is sufficiently trustworthy for an asymmetric decision in which a potentially correct incumbent is discarded.**

This produces a three-level distinction:

```text
LEVEL 1 — CORRECTNESS PREDICTION
“Is the incumbent likely to be wrong?”
             ↓
LEVEL 2 — INTERVENTION
“Is this case worth spending additional computation on?”
             ↓
LEVEL 3 — REPLACEMENT AUTHORIZATION
“Is the evidence strong enough to discard the incumbent?”
```

A signal can perform reasonably at Level 1 and Level 2 while failing at Level 3. That is the specific boundary tested by P6-IP.

### 2.3 Why recent verification work strengthens, rather than weakens, the gap

Recent selective-prediction work shows that simple signals such as executability and structural/self-consistency are materially weaker correctness predictors than stronger reasoning-based verification. TraceSQL similarly demonstrates the value of combining semantic grounding with deterministic SQL-structural evidence while preserving diagnostic provenance.

These findings make the P6-IP gate intentionally conservative to interpret: P6-IP did **not** test the strongest conceivable verifier. It tested a low-cost gate based on validity, successful execution, and structural cues. Therefore the result should be read as:

> **The tested verification layer was insufficient for replacement authorization.**

It should **not** be read as:

> “Verification does not work.”

The distinction is important. A stronger verifier could change the result, and testing such a verifier is outside the frozen Project 1 scope.

### 2.4 Where Gartner fits—and where it does not

Gartner's 2026 material is used only for **industrial relevance and engineering framing**:

- *From Demo to Production: Closing the AI Agent Reliability Gap* argues that enterprise agent reliability is a system-level challenge and highlights scope, autonomy, automated guardrails, monitoring, and error budgets.
- *Analyst Take: Designate a Defensible AI Architect Now* frames Defensible AI and AgentOps as emerging enterprise architecture responsibilities.
- *Gartner Predicts By 2028, Explainable AI Will Drive LLM Observability Investments to 50% for Secure GenAI Deployment* emphasizes explainability and observability as trust layers and calls for monitoring latency, drift, token usage, cost, error rates, and output quality.
- *Accelerating AI Adoption: Product Time to Reliability Built on Trust* frames reliability as a product-level property rather than a late security patch.
- *Engineering Trust: The New Hard Skill Essential for Leading AI* emphasizes challenge, transparency, and shared accountability as engineered properties of AI trust.

These reports support the importance of the project's reliability, traceability, and observability dimensions. They do **not** establish the academic novelty of the harm/rescue mechanism or the P6-IP experiment.

---

## 3. Research Questions and Falsification Logic

### RQ1 — Cost/reliability trade-off
Can an evidence-dependent analytical execution policy reduce expected computational cost while maintaining predefined reliability targets?

### RQ2 — Evidence for intervention
Can intermediate evidence identify cases where additional computation is worthwhile?

### RQ3 — Evidence for replacement
Can the same evidence, combined with executable and structurally valid challenger SQL, safely authorize replacement of the incumbent answer?

### RQ4 — Cross-schema robustness
Does the observed intervention behavior persist on schemas not used as the development partition?

### RQ5 — Defensibility
Can the analytical decision process be reconstructed from machine-readable provenance without relying on post-hoc gold correctness to explain the decision?

### Prespecified falsification/stop rule
P6-IP was not required to “beat the benchmark” in a generic sense. It was required to show a materially better harm-rescue-cost trade-off than the incumbent. The algorithmic line would stop if intervention continued to harm correct incumbents materially more often than it rescued incorrect ones, especially if it also increased cost or degraded aggregate correctness.

This is a deliberate anti-cherry-picking control. A negative result is an allowed scientific outcome.

---

## 4. Experimental Methodology

### 4.1 Benchmark and partitions

The Spider dev artifact contains 1,034 cases. The schema-based holdout procedure with seed 1729 assigns four schemas—`car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`—to a 254-case held-out-schema partition. The remaining 16 schemas form a 780-case development partition.

The 254 cases are therefore **not an independent second copy of the 1,034-case set**. They are a schema-defined partition contained within the original dev artifact. This distinction is enforced in analysis.

Spider is used as a controlled cross-schema analytical execution benchmark. It does **not** establish production enterprise validity by itself.

### 4.2 Frozen execution contract

- total cases: 1,034
- development partition: 780 cases
- held-out-schema partition: 254 cases
- holdout fraction: 20%
- holdout seed: 1729
- official Spider evaluator commit: `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- process-isolated execution
- policy timeout: 150 seconds
- runtime chunks: 12
- controlled inference model: local Ollama `llama3.2:1b`
- Azure/paid model inference: not used
- no holdout result used for policy tuning

### 4.3 Policy ladder

The frozen baseline family is:

- **P0 — Always-LLM incumbent:** baseline analytical policy.
- **P1 — Deterministic-only:** no LLM generation.
- **P2 — Static Hybrid:** fixed deterministic/LLM strategy.
- **P3 — Query-only Complexity Router:** pre-evidence query complexity decision.
- **P4 — Query-only Heuristic Confidence Router:** deterministic confidence-style heuristic.
- **P5 — Post-Evidence Cascade:** evidence-dependent escalation after intermediate execution evidence.

P2 and P3 produced identical behavior under the implemented decision rule and are therefore not treated as independent evidence of two distinct successful mechanisms. P4 is a heuristic policy, not a calibrated confidence estimator.

P5R was then used as a forensic challenger. It strengthened evidence predicates but was not allowed to modify the frozen P0–P5 baseline.

P6-IP was the final controlled challenger. No P7/P8 was created after the prespecified stop rule failed.

### 4.4 P6-IP decision architecture

P6-IP starts from the P0 incumbent and uses only decision-time evidence to decide whether intervention is eligible. An eligible case invokes a challenger. The challenger is accepted only if predefined SQL validity, successful execution, and structural checks pass. If verification fails, the incumbent is preserved.

```text
question
   ↓
P0 incumbent
   ↓
decision-time evidence / risk assessment
   ├── KEEP ─────────────────────────→ preserve incumbent
   │
   └── INTERVENE
          ↓
      challenger SQL
          ↓
      verification gate
       ├── reject ──────────────────→ preserve incumbent
       └── pass ────────────────────→ replace incumbent
```

The design deliberately separates:

- **decision-time evidence:** information available to the policy before replacement;
- **post-hoc evaluation:** official Spider correctness and gold-query comparison used only after execution.

Official correctness is never supplied to the policy.

### 4.5 Verification gate

The P6-IP gate checks:

1. SQL validity;
2. successful execution;
3. structural consistency between the question cues and the challenger SQL.

The structural checks include task-relevant patterns such as ordering for sorting requests, aggregate operations for aggregation requests, grouping/window constructs for “each/every” requests, and extremum constructs for maximum/minimum requests.

This is intentionally a **low-cost structural verification gate**, not a semantic equivalence proof. That distinction is essential to the interpretation of the negative result.

### 4.6 Decision-time versus post-hoc fields

The methodological contract prevents evaluator leakage by separating fields into two classes.

**Decision-time:** question, schema, incumbent SQL, retrieved evidence, evidence provenance, selector reason, intervention decision, challenger SQL, verification inputs, authorization/control metadata.

**Post-hoc:** gold SQL, official evaluator correctness, paired harm/rescue classification, final benchmark outcome.

The latter are used to measure whether the policy worked, not to explain why the policy acted.

### 4.7 Primary and secondary metrics

**Primary:**

- official Spider execution accuracy;
- paired P6-IP versus P0 correctness;
- incumbent harm/rescue;
- reliability-target attainment at 90%, 95%, 97%, and 99%.

**Secondary:**

- intervention rate;
- replacement/rejection/preservation rates;
- mean, median, and P95 latency;
- model calls and token usage;
- execution cost;
- runtime failures and abstention;
- decision-trace completeness;
- evidence provenance completeness.

Because P0 itself achieves only ~24.6% accuracy in this configuration, the 90–99% absolute reliability targets are interpreted as diagnostic constraints, not as claims that any tested policy is production-ready.

### 4.8 Statistical analysis

Correctness comparisons use exact two-sided McNemar tests because policies are evaluated on the same cases. Continuous paired differences use bootstrap confidence intervals. Wilson intervals are used for proportions such as harm and rescue rates.

The analysis does not treat overlapping development/holdout cases as independent samples. The four-schema partition is reported as a held-out-schema corroboration within the same original dev artifact.

---

## 5. Results

### 5.1 Frozen P0–P5 baseline evidence

On all 1,034 cases:

| Policy | Correct | Accuracy |
|---|---:|---:|
| P0 | 254/1034 | 24.565% |
| P1 | 0/1034 | 0.000% |
| P2 | 256/1034 | 24.758% |
| P3 | 256/1034 | 24.758% |
| P4 | 20/1034 | 1.934% |
| P5 | 123/1034 | 11.896% |

P5 reduces mean cost relative to P0 by approximately 9.35%, but at a large reliability loss. P0 is correct on 158 cases where P5 is wrong, while P5 rescues only 27 cases where P0 is wrong. Exact paired McNemar p is approximately 1e-23.

This is the first falsification step: post-evidence escalation does not automatically improve the cost/reliability frontier.

### 5.2 P5R mechanism-forensics result

P5R increases development accuracy relative to P5 from 11.896% to 17.311%, but remains below P0 and increases mean cost. Against P0, P5R is 7.25 percentage points lower in paired accuracy on the full 1,034 cases. Against P5, P5R improves paired accuracy by 5.42 percentage points but increases mean cost by approximately 0.054 cost units per case.

The forensic analysis nevertheless identifies predictive signal in intermediate evidence. A diagnostic model using reason/row/column features achieves approximately 0.696 development cross-validation AUC and approximately 0.791 holdout AUC; the holdout bootstrap AUC interval is approximately [0.731, 0.846]. This model was diagnostic only and was not used to tune P6-IP or the holdout.

This result is important methodologically: **evidence can contain correctness-related signal without being a safe replacement authority.**

### 5.3 P6-IP primary result — development

On the 1,034-case development evaluation:

- P0: 254/1034 = **24.565%**
- P6-IP: 234/1034 = **22.631%**
- paired difference: **-1.934 percentage points**
- P6-IP-only correct: 8
- P0-only correct: 28
- both correct: 226
- neither correct: 772
- exact McNemar p = **0.001193**

P6-IP mean cost is **0.33841** versus **0.26908** for P0, approximately **25.8% higher**. Median latency is 2.10s versus 2.00s; P95 latency is 13.62s versus 5.60s.

### 5.4 P6-IP held-out-schema corroboration

On the 254 held-out-schema cases:

- P0: 60/254 = **23.622%**
- P6-IP: 55/254 = **21.654%**
- paired difference: **-1.969 percentage points**
- P6-IP-only correct: 4
- P0-only correct: 9
- both correct: 51
- neither correct: 190
- exact McNemar p = **0.266846**

P6-IP mean cost is **0.34795** versus **0.26941** for P0, approximately **29.2% higher**. P95 latency is 24.85s versus 7.37s.

### 5.5 Protocol disclosure for the holdout

The historical P6 workflow executed development and held-out cases in the same matrix jobs. Therefore some holdout cases ran before the complete development partition had been aggregated and frozen.

No holdout result was used for tuning, and no policy modification was made after observing the holdout. Nevertheless, the ordering is a protocol deviation. The holdout is therefore reported as **locked observational corroboration, not a fully prospective confirmatory test**.

The development result alone triggers the prespecified stop rule, so the paper does not depend on the protocol-deviant holdout to establish its primary conclusion.

### 5.6 Incumbent harm versus rescue

The key result is not aggregate accuracy alone.

| Partition | Intervention-eligible | P0-correct eligible | P0-wrong eligible | Harm | Rescue | Harm rate | Rescue rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 | 33.87% | 0.75% |
| Holdout | 91 | 16 | 75 | 5 | 1 | 31.25% | 1.33% |

On development, 21 of 62 correct incumbents exposed to intervention are harmed, while only 2 of 268 incorrect incumbents are rescued. The net intervention effect is therefore **-19 correctness-changing cases**.

This asymmetry is the central empirical finding.

### 5.7 Replacement outcomes expose the verification boundary

Development decision records contain 157 challenger replacements and 173 challenger rejections. Of the 157 replacements, 35 occur on cases where P0 was correct, giving a **22.29% harm rate among replacements**.

The problem is therefore not merely that the selector makes mistakes. The replacement gate admits challengers that pass its low-cost checks while still displacing a correct incumbent.

This is precisely why the paper distinguishes:

```text
verification for validity
        ≠
verification for correctness
        ≠
verification for replacement authorization
```

### 5.8 Reliability-target outcome

P6-IP achieves none of the predefined 90%, 95%, 97%, or 99% absolute reliability targets. P0 also does not satisfy these absolute targets in the tested model/benchmark configuration. The targets therefore function as explicit reliability constraints rather than evidence of production readiness.

---

## 6. Mechanism Interpretation: What Failed?

### 6.1 The selector contained signal, but not sufficient actionability

P5R shows that intermediate evidence is not random noise. Evidence categories differ in their association with correctness, and simple diagnostic models can rank cases above chance.

P6-IP then tests the stronger question: can that evidence authorize an asymmetric action? The answer under the tested mechanism is no. The selector exposes many correct incumbents to intervention, and the basic verification layer cannot distinguish enough of those incumbents from cases where replacement is beneficial.

The critical distinction is therefore:

> **Predictive evidence can justify investigation without justifying replacement.**

### 6.2 Incumbent preservation was necessary but not sufficient

P6-IP introduced the first explicit safety control: preserve the incumbent whenever challenger verification fails.

This is methodologically stronger than a plain cascade because the challenger cannot replace the incumbent merely because an escalation path was triggered.

However, the experiment demonstrates that preservation is only as strong as the gate. When the gate accepts an incorrect challenger as valid, execution-successful, and structurally plausible, the preservation mechanism has no further semantic protection.

### 6.3 Why another router is not the scientifically justified next step

P5 and P5R already show that changing escalation logic can move accuracy and cost without solving the asymmetric replacement problem. P6-IP adds incumbent preservation and still fails the harm/rescue criterion.

Creating P7/P8 solely to search for a positive result would therefore turn the experiment into uncontrolled algorithm selection.

The prespecified scientific decision is to stop algorithmic escalation/replacement development in Project 1 and move the exposed measurement problem into evaluation and observability research.

---

## 7. Did Project 1 Solve a Problem or Create a New One?

Project 1 did not solve the broad problem of constructing a universally reliable, low-cost adaptive analytical execution policy. That was never a defensible conclusion from the tested evidence.

It did solve narrower methodological and engineering problems:

1. It established a reproducible baseline hierarchy for P0–P5 under a common evaluator and denominator.
2. It exposed and repaired an official-evaluator case-level integrity problem in frozen P0 artifacts without rerunning LLM inference.
3. It established an explicit schema-level development/holdout partition rather than treating overlapping cases as independent evidence.
4. It converted aggregate policy comparison into incumbent-aware harm/rescue accounting.
5. It demonstrated that an evidence selector can contain correctness-related signal without being safe as a replacement authority.
6. It implemented machine-readable decision traces separating decision-time evidence from post-hoc gold/evaluator outcomes.
7. It produced a prespecified scientific stop decision that prevents indefinite algorithmic iteration after a negative result.

The newly explicit research problem is:

> **What evidence threshold and verification mechanism are sufficient to authorize an asymmetric analytical action when the incumbent may already be correct?**

That problem is not artificial. It is revealed when correctness prediction, intervention, and replacement are treated as distinct decisions.

---

## 8. Defensibility Layer and Gartner Alignment

### 8.1 Why defensibility belongs in the methodology

The Defensibility Layer is not a governance score added after the experiment. It is a methodological control for reconstructing why an analytical agent acted.

The layer asks five questions:

1. What did the agent decide?
2. What evidence did it use?
3. Which policy/risk rule caused the action?
4. Which verification and authorization controls applied?
5. What outcome, cost, latency, and accountability evidence was recorded?

A defensibility record should make the following reconstructable:

- case and schema identity;
- policy and code version;
- model/provider/version;
- dataset and evaluator manifest;
- incumbent SQL;
- decision-time evidence and provenance;
- selector reason;
- KEEP/INTERVENE decision;
- challenger SQL;
- verification checks and outcomes;
- authorization/control hooks where available;
- final outcome class;
- rescue/harm/preservation classification;
- latency, calls, tokens, cost;
- timeout/runtime error;
- timestamp/correlation/reproducibility metadata.

Gold SQL and official correctness remain post-hoc fields. They must not be used as decision-time explanations.

### 8.2 Gartner's Defensible AI relevance

Gartner's 2026 work provides strong external evidence that this direction is industrially relevant:

- Gartner describes AI-agent reliability as a system-level problem and recommends controlling scope/autonomy, using automated guardrails, and monitoring performance through operational controls.
- Gartner's Defensible AI framing treats challenge, transparency, accountability, and specialized architecture responsibilities as necessary for scaling AI.
- Gartner's LLM observability work explicitly moves beyond latency/cost toward output quality, factual/logical correctness, drift, token usage, error rates, and continuous evaluation.
- Gartner's trust-oriented product research frames “time to reliability” as a core product concern rather than treating behavioral failures as an after-the-fact security issue.

Project 1 operationalizes a research-scale subset of those principles: provenance, decision rationale, verification coverage, policy outcome, harm/rescue, cost, latency, reproducibility, and drift-ready trace fields.

The paper does **not** claim that these records constitute legal compliance, complete governance, production AgentOps, or a full Gartner-defined Defensible AI architecture. Gartner is used to establish industrial relevance and design direction, not to validate the academic result.

### 8.3 Why the negative result strengthens the defensibility argument

The most defensible outcome is not “the router worked.” It is:

> **The router reduced neither reliability risk nor cost sufficiently to justify its replacement behavior, and the trace data makes that failure measurable and auditable.**

This is aligned with the broader trust principle that AI autonomy should be earned through demonstrated reliability rather than assumed from model capability.

---

## 9. Limitations and Reviewer Threats

### 9.1 P0 is a weak incumbent

P0 achieves only 24.565% on the 1,034-case development evaluation using `llama3.2:1b`. A reviewer can reasonably argue that a stronger incumbent may produce a different harm/rescue trade-off.

This is a real limitation. The conclusion is therefore conditional on the tested model and benchmark configuration. It is not an impossibility theorem.

The paired intervention analysis remains meaningful because the research question concerns whether the challenger safely replaces the incumbent it actually receives. Nevertheless, stronger models must be tested before generalizing beyond this setting.

### 9.2 The verification gate is weak

The P6-IP gate checks validity, execution, and structural consistency. It does not establish semantic equivalence between incumbent and challenger results, calibrated correctness probability, or independent semantic adjudication.

Recent verification literature makes this limitation explicit: simple executability/structural signals are weaker correctness predictors than stronger reasoning-based verification, and traceable learned verification can combine semantic and structural evidence.

The paper therefore claims only that the **tested verification mechanism** was insufficient for replacement authorization.

### 9.3 Spider is not an enterprise production benchmark

Spider provides controlled cross-schema Text-to-SQL evaluation. It does not represent enterprise authorization systems, business definitions, privacy policies, row-level security, workflow ownership, production data distributions, or human escalation processes.

The correct language is therefore:

> **enterprise-motivated analytical execution framework evaluated on a public cross-schema Text-to-SQL benchmark**

rather than “enterprise production benchmark.”

Enterprise relevance is supported by the architecture and by related enterprise analytics/governance literature, including work such as GROUND, but production validity requires additional datasets and controls.

### 9.4 Holdout protocol deviation

The historical P6 workflow executed holdout cases before complete development aggregation/freeze. No holdout outcome was used for tuning, but the ordering prevents the holdout from being described as a fully prospective confirmatory test.

This limitation is disclosed prominently. Development evidence alone triggers the stop rule.

### 9.5 Implementation-specific failure possibility

The observed harm/rescue asymmetry could be specific to the tested selector, model, verification gate, or challenger generation process. That possibility is valid.

The paper therefore makes a conditional mechanism claim:

> **Under the tested Spider cross-schema setting, the combination of decision-time evidence, incumbent-preserving intervention, and executable/structural verification did not provide a sufficiently favorable harm-rescue trade-off for incumbent replacement.**

### 9.6 Literature-review scope

The supplied literature corpus was used as a novelty-threat inventory. The paper cites the most directly constraining works rather than claiming that every supplied link was subjected to identical full-text methodological analysis. This avoids an unsupported “all papers were deeply reviewed” claim.

---

## 10. Statistical and Evidence Integrity Checks

The statistical conclusions are based on paired case-level outcomes.

### Development P6-IP vs P0

- P6-IP-only correct: 8
- P0-only correct: 28
- paired difference: -1.934 pp
- exact two-sided McNemar p = 0.001193

### Held-out schemas P6-IP vs P0

- P6-IP-only correct: 4
- P0-only correct: 9
- paired difference: -1.969 pp
- exact two-sided McNemar p = 0.266846

The holdout p-value is not interpreted as evidence of improvement or degradation by itself. It is reported as corroborating evidence under the disclosed protocol limitation.

Cost differences are paired continuous comparisons rather than independent-sample comparisons. Proportion intervals use Wilson intervals.

An important artifact-integrity correction was required during analysis: frozen P0 case-level `official_execution_correct` fields were incomplete even though the aggregate frozen results were present. P0 correctness was therefore recomputed **post hoc from the frozen P0 SQL using the pinned official evaluator**, with no LLM inference rerun. The analysis pipeline was hardened to reject missing/non-boolean official labels rather than silently treating them as false.

This correction is part of the scientific evidence chain, not a change to the model or policy.

---

## 11. Scientific Decision and Stop Rule

P6-IP fails the prespecified stop criterion.

### Development

- harm among P0-correct interventions: **33.87%**
- rescue among P0-wrong interventions: **0.75%**
- mean cost change: **+25.8%**
- aggregate accuracy change: **-1.934 pp**
- exact paired McNemar p = **0.001193**

### Held-out schemas

- harm among P0-correct interventions: **31.25%**
- rescue among P0-wrong interventions: **1.33%**
- mean cost change: **+29.2%**
- aggregate accuracy change: **-1.969 pp**

**Decision: stop algorithmic escalation/replacement development in Project 1.**

No P7/P8 should be created merely to recover a positive result.

The project should now prioritize:

- failure-mode characterization;
- evaluator and artifact integrity;
- verification-strength analysis;
- decision-trace completeness;
- cost/reliability/latency measurement;
- policy/model/provider drift observability;
- literature positioning;
- paper finalization;
- transfer of requirements into Project 2.

---

## 12. What Project 1 Feeds into Project 2

Project 2 — Production LLM Evaluation & Observability Platform — should not begin as “another router.” It should inherit the failure boundary discovered here.

```text
PROJECT 1
Analytical execution
        ↓
empirical boundary:
predictive evidence ≠ safe authorization
        ↓
measurement requirements
        ↓
PROJECT 2
Evaluation + Observability
        ↓
measure, attribute, and monitor the gap
```

### 12.1 Research requirements inherited from Project 1

| Project 1 finding | Project 2 requirement |
|---|---|
| Aggregate accuracy hides asymmetric intervention harm | Paired incumbent/challenger evaluation and harm/rescue accounting |
| Evidence contains predictive signal but weak replacement safety | Separate prediction metrics from action-authorization metrics |
| Executable/structurally valid SQL can still be wrong | Verification-strength taxonomy and semantic-correctness gap metrics |
| P0 case-level official labels were initially incomplete | Evaluator-integrity checks, denominator checks, and case-level lineage |
| Holdout ordering matters | Dataset/split lineage and freeze-state enforcement |
| Decision-time and post-hoc fields must remain separate | Oracle-leakage prevention in trace schema |
| Intervention can increase cost | Cost per rescue and cost per harmful intervention |
| P95 latency can worsen despite median stability | Tail-latency observability |
| Policy behavior can change correctness asymmetrically | Policy-level harm/rescue drift |
| Defensibility requires provenance | Reproducible policy/model/evidence lineage |
| Negative result must terminate uncontrolled tuning | Research state machine and stop-rule enforcement |
| Gartner emphasizes observability and trust | Operational metrics for quality, drift, cost, latency, and accountability |

### 12.2 Proposed Project 2 research question

> **Can an evaluation and observability layer detect, attribute, and continuously monitor the gap between evidence that predicts analytical correctness, evidence that justifies additional computation, and evidence that is safe to use for consequential agent actions?**

This is a direct continuation of Project 1 rather than a new unrelated application.

### 12.3 What should be carried into the next repository

The Project 2 handoff should include:

1. P0–P6 benchmark manifest;
2. pinned Spider evaluator commit;
3. case-level correctness schema;
4. decision-record schema;
5. intervention/harm/rescue definitions;
6. evidence provenance contract;
7. verification contract and known weaknesses;
8. cost/latency/token metrics;
9. holdout lineage and freeze rules;
10. research state machine and stop-rule philosophy;
11. failure taxonomy;
12. literature novelty boundary;
13. Gartner/Defensible-AI alignment as engineering context;
14. locked Project 1 results and paper draft.

Project 2 should treat these as requirements derived from empirical failure, not arbitrary dashboard features.

---

## 13. Expected Scientific Continuity Across the Portfolio

### Project 1 — Enterprise Analytics Copilot

**Question:** Can intermediate evidence support cost-aware analytical intervention and safe incumbent replacement?  
**Finding:** Evidence contains predictive signal, but the tested evidence + basic verification mechanism is not safe enough for replacement; harm greatly exceeds rescue and cost increases.

### Project 2 — Production LLM Evaluation & Observability Platform

**Question:** Can we measure, attribute, and monitor when AI evidence is predictive, when it is actionable, and when action becomes unsafe?  
**Expected contribution:** evaluation/observability methods that expose reliability, provenance, drift, verification, cost, latency, and decision asymmetry rather than collapsing them into one score.

### Project 3 — AI Marketing Spend Optimizer

The later optimization project can inherit the evaluation/observability controls from Project 2, especially decision provenance, paired/counterfactual evaluation, uncertainty, cost constraints, and action-risk monitoring.

The portfolio therefore becomes:

```text
P1: Can the agent act safely?
          ↓
P2: Can we measure and observe whether it is acting safely?
          ↓
P3: Can we optimize consequential business actions under those measured constraints?
```

---

## 14. Conclusion

Project 1 does not end with a better router. It ends with a better-defined scientific problem and a falsifiable boundary.

The central empirical observation is:

> **Correctness prediction, intervention eligibility, and replacement authorization are different decisions. Evidence that is informative enough to justify investigation is not necessarily strong enough to justify replacement.**

In the tested Spider cross-schema setting, P6-IP's decision-time evidence plus executable/structural verification harmed correct incumbents substantially more often than it rescued incorrect ones and increased computational cost. Incumbent preservation reduced uncontrolled replacement behavior, but the gate itself was not strong enough to make replacement safe.

The correct interpretation is therefore not “adaptive routing failed” and not “verification is useless.” The supported statement is narrower:

> **Under the tested model, benchmark, evidence class, challenger mechanism, and verification gate, the mechanism did not achieve a sufficiently favorable harm-rescue-cost trade-off for incumbent replacement.**

That result creates a concrete measurement agenda for the next project: make the gap between prediction, intervention, and authorization observable, attributable, reproducible, and monitorable over time.

The Defensibility Layer provides the engineering structure for that transition. Gartner's current emphasis on earned autonomy, system-level reliability, observability, transparency, and accountability reinforces why this measurement discipline matters in enterprise AI systems, while the scientific contribution remains grounded in the controlled experimental evidence rather than in Gartner's industry forecasts.

---

## Appendix A — Locked Evidence References

- P6-IP controlled inference run: `34252265013`
- Frozen P0–P5 source run: `34206500727`
- P0 comparator repair workflow: `34281611836`
- Corrected P6-IP scientific analysis workflow: `34283127475`
- Official Spider evaluator commit: `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- P6-IP implementation branch: `research/p6-ip-defensibility`
- P6-IP result record: `docs/PROJECT1_P6_IP_RESULTS.md`
- Defensibility design: `docs/PROJECT1_DEFENSIBILITY_LAYER.md`
- P6-IP execution contract: `docs/PROJECT1_P6_IP_EXECUTION_HANDOFF.md`

### Appendix A.1 — Directly constraining academic references

1. Robert Richardson. *What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study.* arXiv:2607.06799. https://arxiv.org/abs/2607.06799
2. Paweł Liskowski, Fuheng Zhao, Benjamin Han, Anupam Datta, Dimitris Tsirogiannis. *Compositional Online Learning for Semantic Data Processing Systems.* arXiv:2608.27244. https://arxiv.org/abs/2608.27244
3. Kaiwen Chen, Yueting Chen, Nick Koudas, Xiaohui Yu. *Reliable Text-to-SQL with Adaptive Abstention.* arXiv:2501.10858 / Proc. ACM Manag. Data. https://arxiv.org/abs/2501.10858
4. Zafar Hussain, Kristoffer Nielbo. *The Coverage Illusion: From Pre-retrieval Routing Failure to Post-retrieval Cascades in a Production RAG System.* arXiv:2605.27220. https://arxiv.org/abs/2605.27220
5. Neelesh Kumar Shukla et al. *TraceSQL: Traceable Answerability Estimation for Reference-Free Text-to-SQL Verification.* arXiv:2608.17795. https://arxiv.org/abs/2608.17795
6. Giovanni Sullutrone et al. *ABISS: Evaluating Text-to-SQL Systems Through Agent Interaction.* arXiv:2607.23340. https://arxiv.org/abs/2607.23340
7. Aravind Sasidharan Pillai. *GROUND: Reducing Hallucinations in LLM-Based Enterprise Analytics Through Governed Semantic Definitions.* arXiv:2608.26157. https://arxiv.org/abs/2608.26157

These references are representative of the most direct novelty threats. The full supplied literature corpus remains the broader literature-audit source for the paper's final bibliography.

### Appendix A.2 — Gartner industry-context references

G1. Gartner. *From Demo to Production: Closing the AI Agent Reliability Gap.* 8 May 2026. https://www.gartner.com/en/documents/7832217

G2. Gartner. *Analyst Take: Designate a Defensible AI Architect Now.* 20 May 2026. https://www.gartner.com/en/documents/7887777

G3. Gartner. *Gartner Predicts By 2028, Explainable AI Will Drive LLM Observability Investments to 50% for Secure GenAI Deployment.* 30 March 2026. https://www.gartner.com/en/newsroom/press-releases/2026-03-30-gartner-predicts-by-2028-explainable-ai-will-drive-llm-observability-investments-to-50-percent-for-secure-genai-deployment

G4. Gartner. *Accelerating AI Adoption: Product Time to Reliability Built on Trust.* 12 June 2026. https://www.gartner.com/en/documents/7996037

G5. Gartner. *Engineering Trust: The New Hard Skill Essential for Leading AI.* 7 July 2026. https://www.gartner.com/en/documents/8102697

Gartner references are used as industrial-context evidence for reliability, observability, transparency, accountability, and Defensible AI. They are not used to claim academic novelty.

---

## Appendix B — Claim Discipline

The following statements are intentionally prohibited unless new evidence is produced:

- “Adaptive routing is novel.”
- “Evidence-dependent execution is universally optimal.”
- “Executable SQL is a reliable correctness verifier.”
- “Incumbent-preserving intervention is solved.”
- “The method guarantees 90%/95%/97%/99% reliability.”
- “Spider demonstrates production enterprise readiness.”
- “The result proves no stronger verifier could work.”
- “The literature contains no prior adaptive/cascade/verification methods.”
- “Gartner validates the scientific novelty.”

The supported claim remains empirical and conditional on the tested setting.
