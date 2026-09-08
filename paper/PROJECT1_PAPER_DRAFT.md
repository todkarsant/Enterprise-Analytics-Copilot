# When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents

**Project:** Project 1 — Enterprise Analytics Copilot  
**Status:** Living paper draft; results and claims are locked to the current controlled evidence.  
**Repository branch:** `research/p6-ip-defensibility`  
**Last updated:** 2026-09-09

> **Scientific status:** This paper is intentionally framed as an empirical boundary/failure-mode study. It does not claim that adaptive routing, cascades, verification, or Text-to-SQL are individually novel. The central claim is narrower: in the tested cross-schema analytical setting, intermediate evidence and basic executable/structural verification were not sufficient to authorize safe replacement of a correct incumbent answer.

---

## Abstract

Enterprise analytical agents must balance correctness, computational cost, latency, and operational accountability. A natural strategy is to use intermediate evidence generated during execution to decide whether to spend additional computation or replace an incumbent analytical answer. However, evidence that is useful for identifying risk need not be sufficiently reliable to authorize replacement of an answer that may already be correct.

We study this distinction in an evidence-dependent analytical execution framework evaluated on the Spider benchmark under a frozen, cross-schema protocol. We compare fixed, query-only, confidence-style, and post-evidence cascade policies, then evaluate an incumbent-preserving challenger (P6-IP) that begins from a P0 incumbent, uses decision-time evidence to determine whether to intervene, generates a challenger only for eligible cases, and replaces the incumbent only after predefined SQL validity, execution, and structural checks. The primary outcome is official Spider execution accuracy, complemented by paired harm/rescue analysis, cost, latency, and decision-trace completeness.

The final P6-IP experiment does not improve the incumbent. On the 1,034-case development partition, P0 obtains 254 correct cases (24.565%) versus 234 (22.631%) for P6-IP, a paired difference of -1.934 percentage points (exact McNemar p=0.001193). Among intervention-eligible cases, 33.87% of P0-correct cases are harmed while only 0.75% of P0-wrong cases are rescued; mean cost is 25.8% higher than P0. The held-out-schema partition shows the same direction, with 31.25% harm versus 1.33% rescue among eligible cases and 29.2% higher mean cost. The historical holdout execution occurred before full development aggregation/freeze and is therefore treated as locked observational corroboration rather than a fully prospective confirmatory result.

These results do not show that evidence-dependent analytical intervention is impossible. They establish a more precise boundary: evidence can be sufficiently informative to motivate additional computation while remaining insufficiently trustworthy to authorize incumbent replacement. The study therefore separates three decisions that are often conflated—correctness prediction, intervention, and replacement—and motivates a subsequent evaluation/observability research direction in which decision provenance, evaluator integrity, verification coverage, harm/rescue outcomes, cost, latency, and policy drift are first-class measurable objects.

---

## 1. Introduction

LLM-based analytical agents increasingly combine retrieval, SQL generation, execution, verification, repair, clarification, and escalation. This creates a sequential decision problem: after each execution step, the system has accumulated evidence and must decide what to do next. The tempting formulation is to learn or design a policy that minimizes computational cost while preserving a target level of reliability.

The literature already contains substantial work on adaptive tool use, model routing, cascades, selective prediction, post-retrieval escalation, SQL verification, abstention, and cost-aware sequential computation. Therefore, this work does **not** claim generic adaptive execution as a new idea.

Instead, we ask a narrower reliability question:

> **When an analytical agent obtains intermediate evidence suggesting that its incumbent answer may be incorrect, what evidence is sufficient to justify additional computation, and what evidence is sufficient to justify replacing the incumbent without unacceptable reliability loss?**

This distinction matters because the actions have asymmetric consequences. Spending additional computation on a case that turns out to be correct is primarily a cost error. Replacing a correct incumbent with an incorrect challenger is a reliability error. A policy can therefore be useful as a *risk detector* while being unsafe as a *replacement authority*.

Project 1 was designed to test this boundary rather than assume that a more sophisticated router would necessarily improve the accuracy-cost frontier. The frozen baseline suite (P0–P5) first established the behavior of always-LLM, deterministic-only, static hybrid, query-only routing, heuristic confidence routing, and post-evidence cascade strategies. P5 was retained as the strongest mandatory cascade comparator. A forensic challenger (P5R) then tested whether stricter evidence predicates improved intervention selectivity. Finally, P6-IP introduced incumbent preservation and explicit replacement verification.

The experiment produced a negative result for the proposed replacement mechanism. Importantly, the negative result is not the absence of a contribution. It reveals a previously conflated decision boundary and provides a falsifiable empirical constraint on what intermediate evidence and basic verification can safely authorize.

### Contributions

This paper makes five deliberately bounded contributions:

1. **Decision decomposition.** We distinguish correctness prediction, intervention eligibility, and incumbent replacement as separate reliability decisions.
2. **Incumbent-aware evaluation.** We evaluate analytical intervention using paired harm and rescue outcomes rather than aggregate accuracy alone.
3. **Empirical boundary result.** We show that, in the tested Spider cross-schema setting, executable and structurally valid challenger SQL was not sufficient for safe incumbent replacement.
4. **Reproducible evidence protocol.** We use a frozen evaluator, fixed schema holdout construction, isolated execution, paired statistical tests, and explicit artifact-integrity checks.
5. **Defensibility-oriented trace design.** We record decision-time evidence, policy reasons, verification state, outcome, cost/latency, and provenance separately from post-hoc gold/evaluator labels, providing a direct input to the next evaluation/observability research project.

We explicitly do **not** claim universal optimality, a general impossibility theorem, generic novelty of adaptive routing, or production governance compliance.

---

## 2. Related Work and Novelty Boundary

### 2.1 What is already established

The literature reviewed for Project 1 contains multiple families closely related to this study:

- adaptive tool use and budget-constrained agents;
- LLM routing and cascading;
- post-retrieval or post-generation escalation;
- semantic SQL cascades and execution-aware query processing;
- selective prediction and confidence estimation;
- SQL verification and reference-free answerability checking;
- abstention and human-in-the-loop reliability controls;
- enterprise Text-to-SQL governance, authorization, and observability.

Consequently, the following claims are **not** proposed as novel contributions:

- choosing among tools/actions adaptively;
- reducing cost through routing or cascading;
- using execution or structural signals to estimate correctness;
- verifying SQL before execution;
- abstaining when confidence is low;
- adding governance/audit metadata to an analytical system.

### 2.2 The narrower research gap

The literature is fragmented by where adaptation occurs: before generation, during generation, after retrieval, after SQL generation, inside semantic query execution, or at the generic tool-use layer. Project 1 studies a different unit of analysis: an analytical request as a sequence of heterogeneous operators in which accumulated evidence can trigger an intervention against an incumbent answer.

The critical distinction is not simply whether an evidence signal predicts correctness. It is whether that signal is sufficiently trustworthy for an **asymmetric replacement decision**.

This leads to the paper's central conceptual separation:

```text
Evidence → correctness prediction
         → intervention decision
         → replacement authorization
```

A signal may succeed at the first level and fail at the third. Project 1 provides empirical evidence for exactly this possibility.

### 2.3 Position against the reviewed literature

The strongest novelty threats identified during the literature audit include semantic SQL cascade routing, post-retrieval cascades, SQL answerability verification, selective correctness prediction, enterprise-governed Text-to-SQL, and budget-driven dynamic computation. Project 1 therefore positions itself as a **boundary study across these mechanisms**, not as a replacement for them.

The relevant empirical question is:

> Does a combination of intermediate evidence, intervention eligibility, incumbent preservation, and basic challenger verification create a favorable reliability-cost frontier?

The controlled experiment answers **no under the tested conditions**. That negative result is itself the evidence that narrows the next research question.

---

## 3. Research Questions and Hypotheses

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

### Prespecified decision rule
P6-IP was required to materially reduce incumbent harm while retaining meaningful rescues at defensible cost/reliability. Failure of that condition triggers a stop to algorithm development and a transition to an empirical boundary/failure-mode study.

---

## 4. Experimental Design

### 4.1 Benchmark and partitions

The current Spider dev artifact contains 1,034 cases. The schema-based holdout procedure with seed 1729 assigns four schemas—`car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`—to a 254-case held-out-schema partition. The remaining 16 schemas form a 780-case development partition.

The 254 cases are therefore **not an independent second copy of the full 1,034-case set**. They are a schema-defined partition contained within the original dev artifact. This distinction is enforced in reporting.

### 4.2 Frozen execution contract

- Spider cases: 1,034 total
- development partition: 780 cases
- held-out-schema partition: 254 cases
- holdout fraction: 20%
- holdout seed: 1729
- official Spider evaluator commit: `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- isolated process execution
- policy timeout: 150 seconds
- runtime chunks: 12
- iteration model: local Ollama `llama3.2:1b`
- Azure/paid models: not used for the controlled experiment

### 4.3 Policies

The frozen baseline family is:

- **P0:** Always-LLM incumbent
- **P1:** Deterministic-only
- **P2:** Static hybrid
- **P3:** Query-only complexity router
- **P4:** Query-only heuristic confidence router
- **P5:** Post-evidence cascade

P2 and P3 produced identical behavior under the implemented decision rule and should therefore not be interpreted as independent evidence of two distinct successful mechanisms. P4 is a heuristic policy, not a calibrated confidence estimator.

P5R was used as a forensic mechanism challenger and did not replace the frozen baseline.

P6-IP was the final controlled challenger.

### 4.4 P6-IP mechanism

P6-IP starts from the P0 incumbent and uses only evidence available at decision time to determine whether intervention is eligible. An eligible case invokes a challenger. Challenger acceptance requires predefined SQL validity, successful execution, and structural checks. If verification fails, the incumbent is preserved.

Conceptually:

```text
question
   ↓
P0 incumbent
   ↓
evidence / risk assessment
   ├── KEEP ─────────────────────→ incumbent
   │
   └── INTERVENE
          ↓
      challenger
          ↓
      verification
       ├── reject ───────────────→ preserve incumbent
       └── pass ─────────────────→ replace incumbent
```

Official evaluator correctness is strictly post hoc. It is not exposed to the policy.

### 4.5 Primary and secondary metrics

Primary:

- official Spider execution accuracy;
- paired P6-IP vs P0 correctness;
- reliability-target attainment at 90%, 95%, 97%, and 99%.

Secondary:

- incumbent harm: P0 correct → challenger/final policy wrong;
- rescue: P0 wrong → challenger/final policy correct;
- intervention rate;
- replacement and rejection rates;
- mean/median/P95 latency;
- model calls and token usage;
- execution cost;
- runtime failure and abstention;
- decision-trace completeness and provenance completeness.

### 4.6 Statistical analysis

Paired correctness comparisons use exact two-sided McNemar tests because the same cases are evaluated under each policy. Bootstrap confidence intervals are used for paired cost and other continuous differences. Wilson intervals are used for proportions such as intervention harm/rescue rates.

No holdout result is used for policy tuning.

---

## 5. Results

### 5.1 Frozen P0–P5 baseline evidence

On all 1,034 cases, official execution accuracy was:

| Policy | Correct | Accuracy |
|---|---:|---:|
| P0 | 254/1034 | 24.565% |
| P1 | 0/1034 | 0.000% |
| P2 | 256/1034 | 24.758% |
| P3 | 256/1034 | 24.758% |
| P4 | 20/1034 | 1.934% |
| P5 | 123/1034 | 11.896% |

P5 reduced mean cost relative to P0 by approximately 9.35%, but at a large reliability loss. P0 was correct on 158 cases where P5 was wrong, while P5 rescued only 27 cases where P0 was wrong. The exact paired McNemar p-value was approximately 1e-23.

This baseline result already rejects a simple interpretation in which post-evidence escalation automatically creates a better cost/reliability frontier.

### 5.2 P5R forensic result

P5R increased development accuracy relative to P5 from 11.896% to 17.311%, but remained below P0 and increased mean cost. Against P0, P5R was 7.25 percentage points lower in paired accuracy on the full 1,034 cases. Against P5, P5R improved paired accuracy by 5.42 percentage points but increased mean cost by approximately 0.054 cost units per case.

The result suggested that stricter evidence predicates contain useful signal but do not solve incumbent replacement. This motivated the final incumbent-preserving P6-IP experiment rather than another routing heuristic.

### 5.3 P6-IP primary result

#### Development partition: 1,034 cases

- P0: 254/1034 = **24.565%**
- P6-IP: 234/1034 = **22.631%**
- paired difference: **-1.934 percentage points**
- P6-IP-only correct: 8
- P0-only correct: 28
- both correct: 226
- neither correct: 772
- exact McNemar p = **0.001193**

P6-IP mean cost was **0.33841** versus **0.26908** for P0, approximately **25.8% higher**. Median latency was 2.10s versus 2.00s; P95 latency was 13.62s versus 5.60s.

#### Held-out schemas: 254 cases

- P0: 60/254 = **23.622%**
- P6-IP: 55/254 = **21.654%**
- paired difference: **-1.969 percentage points**
- P6-IP-only correct: 4
- P0-only correct: 9
- both correct: 51
- neither correct: 190
- exact McNemar p = **0.266846**

P6-IP mean cost was **0.34795** versus **0.26941** for P0, approximately **29.2% higher**. P95 latency was 24.85s versus 7.37s.

The holdout run is retained as locked observational corroboration. It is **not** treated as a fully prospective confirmatory run because the historical workflow executed holdout cases before the complete development partition had been aggregated and frozen. Development evidence alone already triggers the prespecified stop rule.

### 5.4 Incumbent harm versus rescue

The key result is not aggregate accuracy alone. P6-IP produced the following intervention outcomes.

| Partition | Eligible | P0-correct eligible | P0-wrong eligible | Harm | Rescue | Harm rate | Rescue rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 | 33.87% | 0.75% |
| Holdout | 91 | 16 | 75 | 5 | 1 | 31.25% | 1.33% |

On development, 21 of 62 correct incumbents exposed to intervention were ultimately harmed, while only 2 of 268 incorrect incumbents were rescued. The net intervention effect was therefore -19 correctness-changing cases.

This asymmetry is the central empirical finding.

### 5.5 Why executable SQL was not enough

The P6-IP challenger gate required SQL validity, successful execution, and structural consistency with detected question cues. These checks reduced some obviously invalid candidates, but the final outcomes show that passing them was not equivalent to semantic correctness or replacement safety.

The result is therefore not:

> "SQL verification is useless."

The supported conclusion is:

> **The tested verification layer was insufficiently strong for the asymmetric decision of replacing a potentially correct incumbent.**

This distinction prevents the negative result from being misread as a general rejection of verification.

### 5.6 Reliability target outcome

P6-IP achieved none of the predefined 90%, 95%, 97%, or 99% reliability targets. P0 itself also does not satisfy these absolute targets on this benchmark/model configuration; the targets are therefore interpreted as decision constraints rather than evidence that any tested policy is production-ready.

---

## 6. Did Project 1 Solve a Problem or Create a New One?

### 6.1 What problem was solved?

Project 1 did not solve the original broad problem of constructing a universally reliable, low-cost adaptive analytical execution policy. The experiment was designed to falsify that possibility under a concrete implementation and benchmark protocol rather than assume success.

It **did solve several narrower research and engineering problems**:

1. It established a reproducible baseline hierarchy for P0–P5 under a common evaluator and denominator.
2. It exposed and repaired a case-level official-evaluator integrity problem in the frozen P0 artifacts without rerunning LLM inference.
3. It established an explicit schema-level development/holdout partition instead of treating overlapping cases as independent evidence.
4. It converted aggregate policy comparison into an incumbent-aware harm/rescue analysis.
5. It demonstrated that an intervention selector can contain correctness-related signal without being safe as a replacement authority.
6. It implemented machine-readable decision traces separating decision-time evidence from post-hoc gold/evaluator outcomes.
7. It produced a prespecified scientific stop decision, preventing uncontrolled algorithmic iteration after a negative result.

These are concrete outputs even though the proposed replacement policy failed.

### 6.2 Did we create a new problem?

Not in the sense of inventing an artificial problem. The experiment **uncovered a latent problem that was hidden when correctness prediction and action authorization were treated as the same task**.

The newly explicit problem is:

> **What evidence threshold and verification mechanism are sufficient to authorize an asymmetric analytical action when the incumbent may already be correct?**

This is a sharper problem than the original routing question because it recognizes that the cost of a false intervention is not symmetric with the cost of unnecessary computation.

### 6.3 How was the newly exposed problem addressed?

P6-IP attempted the first necessary control: incumbent preservation. It prevented replacement whenever the challenger failed predefined checks. The experiment then demonstrated that this control was insufficient because the verification gate itself admitted too many harmful replacements and produced very few rescues.

Therefore the problem is **not solved by adding another heuristic router**. The scientifically justified next step is to improve the measurement and observability of evidence quality, verification strength, policy behavior, and decision outcomes before proposing another replacement algorithm.

That is the bridge to Project 2.

---

## 7. Interpretation: Correctness Prediction ≠ Intervention ≠ Replacement

Project 1 supports the following three-level model:

```text
Level 1: Can evidence predict whether the incumbent is correct?
             ↓
Level 2: Is the case worth spending additional computation on?
             ↓
Level 3: Is the evidence strong enough to authorize replacing the incumbent?
```

The experiments provide evidence that these levels should not be collapsed.

P5R's forensic analysis found predictive signal in intermediate evidence features. A simple diagnostic model using reason/row/column features achieved a development cross-validation AUC of approximately 0.696 and a holdout AUC of approximately 0.791, with a bootstrap holdout AUC interval of roughly [0.731, 0.846]. These are diagnostic findings only; the model was not used to tune P6-IP or the holdout.

Yet P6-IP, which used evidence-triggered intervention plus basic verification, produced 33.87% harm versus 0.75% rescue among eligible development cases. Thus a signal can be predictive enough to justify **investigation** without being reliable enough to justify **replacement**.

This is the paper's most important conceptual result.

---

## 8. Defensibility Layer

The Defensibility Layer is intentionally separate from the primary scientific claim. It records the evidence needed to reconstruct an analytical decision:

1. What did the agent decide?
2. What evidence did it use?
3. Which policy/risk rule caused the action?
4. Which verification and authorization controls applied?
5. What outcome, cost, latency, and accountability evidence was recorded?

A decision record contains case identity, schema, policy/code version, model/provider information, dataset/evaluator manifest, incumbent SQL, decision-time evidence and provenance, selector reason, intervention decision, challenger SQL, verification checks, final decision, outcome class, runtime state, latency/tokens/calls/cost, and reproducibility metadata.

Crucially, gold SQL and official evaluator correctness remain post-hoc fields. This prevents oracle leakage and makes it possible to audit whether a policy actually had access to the evidence it is claimed to use.

The layer should be described as **defensible engineering evidence**, not as proof of legal compliance, complete governance, production readiness, or human-factors explainability.

---

## 9. Limitations and Reviewer Threats

### 9.1 Weak incumbent/model capability

P0 achieves only 24.565% on the 1,034-case development partition. The model is `llama3.2:1b`. A reviewer can reasonably argue that replacement behavior may differ with a stronger incumbent.

Therefore the result is not an impossibility theorem. It is a measured boundary under the tested model and benchmark configuration.

### 9.2 Verification strength

The P6-IP verification gate is deliberately simple: SQL validity, execution success, and structural checks. It does not establish semantic equivalence between incumbent and challenger answers. A stronger verifier could change the result.

This is a limitation and also the precise reason the paper claims **verification insufficiency in the tested design**, not insufficiency of verification in general.

### 9.3 Spider is not an enterprise production benchmark

Spider provides cross-schema Text-to-SQL evaluation, not real enterprise authorization, business definitions, privacy controls, workflow ownership, or production data distributions. Enterprise relevance is therefore architectural/methodological rather than a claim of production benchmark validity.

### 9.4 Holdout protocol deviation

The historical P6 workflow executed holdout cases before the complete development partition had been aggregated and frozen. No holdout outcome was used to tune the policy, but this ordering defect prevents the holdout from being described as a fully prospective confirmatory run. The primary stop decision is based on development evidence and does not depend on the holdout.

### 9.5 Implementation-specific failure possibility

A reviewer may argue that the observed harm/rescue asymmetry is specific to the selector and verification implementation. This is valid. The paper therefore treats the result as a failure-mode boundary for the tested mechanism, not as a universal impossibility result.

---

## 10. Scientific Decision and Stop Rule

The P6-IP stop rule failed on development data and was directionally corroborated on the held-out schemas.

**Decision: stop algorithmic escalation/replacement development in Project 1.**

No P7/P8 should be created merely to recover a positive result.

The project should now prioritize:

- failure-mode characterization;
- evaluator and artifact integrity;
- verification-gap analysis;
- decision-trace completeness;
- cost/reliability/latency measurement;
- policy drift and model/provider drift observability;
- literature positioning;
- paper finalization;
- transfer of the resulting research requirements into Project 2.

---

## 11. What Project 1 Feeds into Project 2

The originally planned portfolio sequence placed **Project 2 — Production LLM Evaluation & Observability Platform** after the Enterprise Analytics Copilot. Project 1 now provides a much sharper research specification for that repository.

The transfer is not "build another router." It is:

```text
PROJECT 1
Enterprise analytical execution
        ↓
empirical boundary:
 evidence can be predictive without being safe authorization
        ↓
measurement requirements
        ↓
PROJECT 2
Evaluation + Observability
        ↓
next research paper
```

### 11.1 Project 2 research inputs

Project 2 should inherit these requirements as first-class objects:

| Project 1 finding | Project 2 input |
|---|---|
| Aggregate accuracy hides intervention harm | Paired incumbent/challenger evaluation and harm/rescue accounting |
| Intermediate evidence has predictive signal but weak replacement safety | Separate prediction metrics from action-authorization metrics |
| Executable/structurally valid SQL can still be wrong | Verification coverage and semantic-correctness gap metrics |
| P0 case-level official labels were initially incomplete | Evaluator integrity checks, denominator checks, case-level provenance |
| Holdout must not be treated as tuning evidence | Dataset/split lineage and freeze-state enforcement |
| Decision-time and post-hoc fields must be separated | Oracle-leakage prevention in trace schema |
| Intervention can increase cost | Cost per rescued case, cost per harmful intervention, frontier analysis |
| P95 latency can worsen despite median improvement | Tail-latency observability |
| Policy behavior changes correctness asymmetrically | Policy-level drift and harm/rescue drift |
| Defensibility requires provenance | Reproducible decision traces and policy/model/version lineage |
| Basic verification was insufficient | Verification-strength taxonomy and rejection diagnostics |
| Negative result triggered a scientific stop rule | State-machine-based experiment governance and no-cherry-picking controls |

### 11.2 Proposed Project 2 research question

The next paper should not begin with "Can we route better?" A better starting point is:

> **Can an evaluation and observability layer detect, attribute, and continuously monitor the gap between evidence that predicts analytical correctness and evidence that is safe to use for consequential agent actions?**

This creates a clean scientific continuation:

- Project 1 asks whether evidence-dependent intervention can safely improve analytical execution.
- Project 1 finds that prediction signal does not automatically imply replacement safety.
- Project 2 asks how to **measure, observe, attribute, and govern that gap** across models, policies, tools, datasets, and time.

### 11.3 What should be carried into the next repository

The next repository should receive a versioned handoff containing:

1. the P0–P6 benchmark manifest;
2. the frozen Spider evaluator commit;
3. case-level correctness schema;
4. decision-record schema;
5. intervention/harm/rescue definitions;
6. evidence provenance contract;
7. verification contract and known weaknesses;
8. cost/latency/token metrics;
9. holdout lineage and freeze rules;
10. research-state machine and stop-rule philosophy;
11. failure taxonomy;
12. literature novelty boundary;
13. the Project 1 paper draft and locked results.

Project 2 should treat these as **requirements derived from empirical failure**, not as arbitrary dashboard features.

---

## 12. Expected Scientific Continuity Across the Portfolio

The portfolio can now be expressed as a sequence of increasingly defensible questions rather than three disconnected applications:

### Project 1 — Enterprise Analytics Copilot
**Question:** Can intermediate evidence support cost-aware analytical intervention and safe incumbent replacement?  
**Finding:** Evidence can support intervention reasoning, but the tested evidence + basic verification mechanism was not safe enough for replacement; harm greatly exceeded rescue.

### Project 2 — Production LLM Evaluation & Observability Platform
**Question:** Can we reliably measure, attribute, and monitor when AI evidence is predictive, when it is actionable, and when action becomes unsafe?  
**Expected contribution:** evaluation/observability methods that expose reliability, provenance, drift, verification, cost, latency, and decision asymmetry rather than collapsing them into one score.

### Project 3 — AI Marketing Spend Optimizer
The later optimization project can then inherit the evaluation/observability controls from Project 2, especially decision provenance, counterfactual/paired evaluation, uncertainty, cost constraints, and action-risk monitoring. The optimization system should not be built as an isolated recommender; it should consume the defensibility/evaluation discipline established by Projects 1 and 2.

This creates a coherent progression:

```text
P1: Can the agent act safely?
          ↓
P2: Can we measure and observe whether it is acting safely?
          ↓
P3: Can we optimize consequential business actions under those measured constraints?
```

---

## 13. Conclusion

Project 1 does not end with a better router. It ends with a better-defined scientific problem.

The central empirical observation is that **correctness prediction, intervention eligibility, and replacement authorization are different tasks**. In the tested setting, intermediate evidence and basic executable/structural verification were not sufficient to make the third decision safely. P6-IP harmed correct incumbents substantially more often than it rescued incorrect ones and increased cost.

That result prevents an easy but scientifically weak conclusion such as "add more routing." Instead, it establishes a measurable boundary and identifies the missing capability: stronger evidence about semantic correctness and a reliable way to connect evidence quality to asymmetric action risk.

The next research stage should therefore move from algorithmic escalation to evaluation and observability. The purpose of Project 2 is not merely operational monitoring. It is to turn the Project 1 failure boundary into a measurable research object: the gap between **what evidence predicts**, **what evidence justifies intervention**, and **what evidence is sufficient to authorize consequential action**.

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

## Appendix B — Claim Discipline

The following statements are intentionally prohibited unless new evidence is produced:

- "Adaptive routing is novel."
- "Evidence-dependent execution is universally optimal."
- "Executable SQL is a reliable correctness verifier."
- "Incumbent-preserving intervention is solved."
- "The method guarantees 90%/95%/97%/99% reliability."
- "Spider demonstrates production enterprise readiness."
- "The result proves no stronger verifier could work."
- "The literature contains no prior adaptive/cascade/verification methods."

The paper's supported claim remains empirical and conditional on the tested setting.
