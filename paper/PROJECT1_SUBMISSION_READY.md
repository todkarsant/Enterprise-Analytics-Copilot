# When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents

**Project 1 — Enterprise Analytics Copilot**  
**Manuscript status:** Submission-ready research draft; empirical claims locked to executed evidence.  
**Target format:** arXiv-compatible preprint / Nature-style initial manuscript structure.  
**Branch:** `research/p6-ip-defensibility`

> **Claim discipline.** This manuscript is an empirical boundary/failure-mode study. It does not claim novelty for adaptive routing, cascades, selective prediction, SQL verification, abstention, Text-to-SQL, or enterprise governance individually. The central claim is narrower: **under the tested cross-schema setting, decision-time evidence combined with low-cost executable/structural verification was not sufficient to authorize safe incumbent replacement.**

---

## Summary

Enterprise analytical agents increasingly combine retrieval, SQL generation, execution, verification, repair, clarification and escalation. A natural design is to use intermediate evidence to decide whether more computation is justified. The difficulty is that the evidence useful for detecting risk may not be reliable enough to authorize an asymmetric action: discarding an incumbent answer that is already correct.

This study tests that boundary. We first evaluate fixed, query-only and post-evidence policies (P0–P5), then perform mechanism forensics (P5R), and finally evaluate an incumbent-preserving challenger (P6-IP). P6-IP begins with a frozen P0 incumbent, uses only decision-time evidence to determine intervention eligibility, generates a challenger for eligible cases, and replaces the incumbent only after SQL validity, execution and structural verification checks. Correctness is evaluated only post hoc with the pinned official Spider evaluator.

On 1,034 development cases, P0 is correct on 254 cases (24.565%) and P6-IP on 234 (22.631%), a paired difference of −1.934 percentage points (exact McNemar p=0.001193). Among intervention-eligible cases, P6-IP harms 21 of 62 P0-correct incumbents (33.87%) but rescues only 2 of 268 P0-wrong incumbents (0.75%). Mean cost is 25.8% higher than P0. On the 254 held-out-schema cases, the same direction is observed: 31.25% harm versus 1.33% rescue among eligible cases, with 29.2% higher mean cost. Because the historical holdout execution preceded complete development aggregation/freeze, it is reported only as locked observational corroboration, not as a fully prospective confirmatory test.

The result does not show that adaptive intervention or verification is impossible. It identifies a mechanism boundary: **evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.** This distinction separates three decisions that are often conflated: correctness prediction, intervention, and replacement authorization.

The study also introduces a Defensibility Layer that records decision-time evidence, provenance, policy rationale, verification, authorization hooks, outcome, cost, latency and reproducibility separately from post-hoc evaluator labels. Gartner's 2026 work on Defensible AI, agent reliability, trust engineering and AI evaluation/observability is used as industry-context evidence for the importance of these controls, not as evidence of academic novelty.

---

## 1. Introduction

### The problem in one picture

```text
                         ANALYTICAL AGENT
                              │
                              ▼
                         user question
                              │
                              ▼
                     intermediate evidence
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
             predict      intervene     replace
             risk?        now?          incumbent?
                 │            │            │
                 └────────────┴────────────┘
                              │
                     Are these really the
                       same decision?
                              │
                              ▼
                             NO
```

Modern LLM-based analytical systems make sequential decisions. A system may retrieve schema information, generate SQL, execute it, inspect errors or results, verify structural properties, repair the query, ask for clarification, or escalate to a more capable agent. Research on adaptive tool use, routing, cascading, selective prediction, SQL verification and enterprise governance has already established many components of this design space [1–12].

The scientific question is therefore not whether an analytical agent can adapt. It is whether **evidence that is useful for deciding to investigate a case is also strong enough to authorize replacing an incumbent answer**.

The distinction is consequential because the error costs are asymmetric:

```text
Unnecessary intervention
        │
        └── cost / latency error

Wrong replacement of a correct incumbent
        │
        └── reliability error

Correcting a wrong incumbent
        │
        └── reliability benefit
```

A policy can therefore be a useful *risk detector* while being unsafe as a *replacement authority*.

### Research question

> **When an analytical agent obtains intermediate evidence suggesting that its incumbent answer may be incorrect, what evidence is sufficient to justify additional computation, and what evidence is sufficient to justify replacing the incumbent without unacceptable reliability loss?**

The experimental version is narrower:

> **Under cross-schema Text-to-SQL workloads, does an evidence-triggered incumbent-preserving intervention policy using executable and structural verification improve the harm–rescue–cost trade-off relative to a frozen incumbent analytical policy?**

### What this paper does not claim

This paper does **not** claim that it invented:

- adaptive routing;
- sequential decision making;
- post-retrieval or post-evidence cascades;
- Text-to-SQL verification;
- confidence estimation;
- abstention;
- enterprise semantic governance;
- agentic Text-to-SQL.

Those are established areas in the supplied literature corpus [1–24].

Instead, the paper makes a narrower empirical contribution: it **separates prediction, intervention and replacement authorization and measures their asymmetry explicitly**.

---

## 2. Literature Threat Model

### 2.1 Why the literature was treated adversarially

The supplied corpus contains 53 paper links as provided for this research review; the repository audit reports 54 unique arXiv identifiers after removing one duplicate (`2608.13384`). The audit also records that not every supplied item was fully text-verified. Accordingly, this manuscript does not claim “53 papers deeply read” or “54 papers exhaustively verified.” Instead, the corpus is used as a **novelty threat model**, while claims are supported by the directly verified references listed below.

The literature clusters into the following families:

| Family | Established capability | Consequence for Project 1 |
|---|---|---|
| Adaptive tool use | Select when tools are needed. | Adaptive action selection is not novel. |
| Routing and cascading | Defer expensive models/actions until needed. | Cost-aware routing is not novel. |
| Post-evidence cascades | Use retrieval/execution outcomes before escalating. | Evidence-conditioned escalation is not novel in isolation. |
| Semantic SQL cascades | Make execution-time cost/quality decisions around semantic SQL. | Generic adaptive SQL routing is not novel. |
| Selective prediction | Predict correctness and abstain selectively. | Correctness prediction is distinct from action authorization. |
| SQL verification | Use structural, execution and learned verification signals. | Verification itself is not novel. |
| Abstention | Avoid unsafe answers or defer to humans. | Preservation/abstention is an established safety direction. |
| Enterprise governance | Enforce metrics, joins, filters, access and cost constraints. | “Enterprise” requires more than Spider accuracy. |
| Interactive Text-to-SQL | Resolve ambiguity/unanswerability through interaction. | Evidence can indicate uncertainty without uniquely determining replacement. |
| Multi-turn/context optimization | Improve analytical context using memory and historical artifacts. | Context construction is another established axis. |

### 2.2 The closest novelty threats

**Post-evidence escalation.** *The Coverage Illusion* shows that the need for expensive augmentation can become visible only after retrieval, and evaluates a cheapest-first post-retrieval cascade in production [4]. This makes P5 a mandatory comparator rather than an optional baseline.

**Semantic SQL adaptive routing.** *Compositional Online Learning for Semantic Data Processing Systems* makes execution-time decisions and includes semantic SQL cascade routing [5]. A claim that Project 1 merely “routes analytical work dynamically” would therefore be inadequate.

**Correctness prediction.** *What Predicts Correctness in Text-to-SQL?* shows that executability and structural/self-consistency signals are weaker correctness predictors than stronger verification-based signals, with cross-schema verifier generalization remaining difficult [1]. This directly constrains the interpretation of the P6-IP gate.

**Traceable verification.** TraceSQL uses explicit diagnostic features for reference-free Text-to-SQL verification [2]. Therefore traceable evidence itself cannot be claimed as the paper's novel method.

**Abstention.** Reliable Text-to-SQL with Adaptive Abstention demonstrates that abstention and human-in-the-loop control are established reliability mechanisms [6]. P6-IP is therefore evaluated as a replacement experiment, not as the invention of “safe abstention.”

**Enterprise governance.** GROUND constrains metrics, joins, grain, filters, security and cost rules in enterprise analytics [7]. Beyond Text-to-SQL similarly argues for governed enterprise analytics APIs [13], while RBAC-aware Text-to-SQL benchmarking shows that unrestricted benchmark accuracy can conceal access-control failures [14].

### 2.3 The actual gap

The literature strongly supports three questions, but they are not identical:

```text
LEVEL 1 — PREDICTION
Is the incumbent likely to be wrong?

          ↓

LEVEL 2 — INTERVENTION
Is additional computation worth its cost?

          ↓

LEVEL 3 — AUTHORIZATION
Is the evidence strong enough to discard the incumbent?
```

Project 1 tests whether a signal useful for Level 1/2 is sufficient for Level 3.

The paper's central proposition is therefore:

> **Evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.**

That proposition is falsifiable because replacement creates observable paired outcomes: rescue, harm, preservation of a correct incumbent, or preservation of a wrong incumbent.

---

## 3. Research Design

### 3.1 Falsification sequence

The research was deliberately staged so that each experiment could invalidate the next step.

```text
LITERATURE AUDIT
      │
      ▼
Reject broad “adaptive routing is novel” claim
      │
      ▼
FROZEN P0–P5 BASELINES
      │
      ├── P5 fails to beat P0
      ▼
MECHANISM FORENSICS (P5R)
      │
      ├── evidence contains signal
      ├── selector still loses to P0
      ▼
INCUMBENT-PRESERVING P6-IP
      │
      ├── preserve incumbent if gate fails
      ├── measure harm/rescue
      ▼
STOP RULE
      │
      └── harm ≫ rescue + cost ↑
             ↓
      STOP ALGORITHMIC ESCALATION
```

The purpose of P6-IP was not to produce a positive result at any cost. It was the final controlled experiment capable of distinguishing “routing is imperfect” from “the evidence/verification mechanism is not safe enough for asymmetric replacement.”

### 3.2 Benchmark and partitions

The Spider dev artifact contains 1,034 cases. A schema-level split with seed 1729 assigns four schemas—`car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`—to a 254-case held-out-schema partition. The remaining 16 schemas form a 780-case development partition.

The 254 cases are therefore a partition of the 1,034-case artifact, not an independent second dataset.

Spider provides a controlled cross-schema Text-to-SQL setting. It does **not** establish production enterprise readiness, real authorization correctness, or organizational governance by itself. Enterprise relevance is therefore framed as methodological/architectural rather than as a benchmark claim [7,13,14].

### 3.3 Frozen execution contract

| Item | Locked value |
|---|---|
| Total cases | 1,034 |
| Development partition | 780 |
| Held-out schemas | 254 |
| Holdout fraction | 20% |
| Seed | 1729 |
| Official evaluator | Spider commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c` |
| Execution | Process-isolated |
| Timeout | 150 s |
| Chunks | 12 |
| Model | Ollama `llama3.2:1b` |
| Paid/Azure inference | Not used |

### 3.4 Policy ladder

```text
P0  Always-LLM incumbent
 │
 ├── P1  Deterministic-only
 ├── P2  Static Hybrid
 ├── P3  Query-only Complexity Router
 ├── P4  Query-only Heuristic Confidence Router
 │
 └── P5  Post-Evidence Cascade
          │
          ▼
       P5R forensic selector
          │
          ▼
       P6-IP incumbent-preserving challenger
```

P2 and P3 produced identical behavior under the implemented decision rule and are not interpreted as independent evidence of two distinct successful mechanisms. P4 is a heuristic, not a calibrated confidence estimator.

### 3.5 P6-IP mechanism

P6-IP begins from P0 rather than selecting a replacement from scratch.

```text
                 P0 INCUMBENT
                      │
                      ▼
             decision-time evidence
                      │
             ┌────────┴────────┐
             ▼                 ▼
           KEEP            INTERVENE
             │                 │
             │                 ▼
             │            challenger SQL
             │                 │
             │                 ▼
             │          verification gate
             │            ┌────┴────┐
             │            ▼         ▼
             │         REJECT     PASS
             │            │         │
             └────────────┴─────────┤
                                    ▼
                           preserve / replace
```

The gate checks:

1. SQL validity;
2. successful execution;
3. structural consistency with detected question requirements.

It does **not** establish semantic equivalence between incumbent and challenger results.

### 3.6 Decision-time versus post-hoc separation

```text
DECISION TIME                         POST HOC
─────────────                         ────────
Question                              Gold SQL
Schema                                Official correctness
Evidence                              Paired outcome
Evidence provenance                   Statistical analysis
Selector reason
KEEP / INTERVENE
Challenger SQL
Verification result
```

This separation prevents the evaluator from becoming an oracle inside the policy.

### 3.7 Primary metrics

**Primary:**

- official Spider execution accuracy;
- paired P6-IP versus P0 correctness;
- incumbent harm;
- rescue;
- intervention rate;
- mean cost;
- latency.

**Secondary:**

- replacement/rejection rate;
- model calls and tokens;
- P50/P95/P99 latency;
- runtime failures;
- decision-trace completeness;
- evidence provenance completeness.

### 3.8 Statistical tests

Because the same cases are evaluated by both policies, paired correctness comparisons use exact two-sided McNemar tests. Continuous paired differences use bootstrap confidence intervals. Wilson intervals are used for intervention harm/rescue proportions.

The 90/95/97/99% reliability targets are retained as predefined diagnostic targets. They are not interpreted as attainable production guarantees because the tested P0 itself is far below those values.

---

## 4. Results

### 4.1 Frozen P0–P5 baseline

| Policy | Correct / 1034 | Accuracy |
|---|---:|---:|
| P0 | 254 | 24.565% |
| P1 | 0 | 0.000% |
| P2 | 256 | 24.758% |
| P3 | 256 | 24.758% |
| P4 | 20 | 1.934% |
| P5 | 123 | 11.896% |

P5 reduced mean cost by approximately 9.35% relative to P0, but at a large accuracy loss. P0 was correct while P5 was wrong on 158 cases; P5 rescued only 27 cases where P0 was wrong. Exact McNemar p≈1×10⁻²³.

**Interpretation:** simply observing intermediate evidence and escalating when the cascade believes it is necessary did not produce a better reliability-cost frontier in this setting.

### 4.2 P5R forensic result

P5R improved over P5 but did not recover P0.

- P5R: 179/1034 = 17.311%.
- P5R vs P0 paired difference: −7.253 percentage points.
- P5R vs P5 paired improvement: +5.416 percentage points.
- P5R increased cost relative to P5.

Diagnostic evidence models found predictive signal in evidence features, but the selector was not sufficiently aligned with P0 correctness to safely authorize replacement.

This motivated P6-IP: **do not replace unless the incumbent is explicitly preserved when the challenger cannot pass a predefined gate.**

### 4.3 P6-IP: development

| Metric | P0 | P6-IP |
|---|---:|---:|
| Correct | 254/1034 | 234/1034 |
| Accuracy | 24.565% | 22.631% |
| Mean cost | 0.26908 | 0.33841 |
| Median latency | 2.001 s | 2.100 s |
| P95 latency | 5.603 s | 13.616 s |

Paired outcome counts:

```text
                    P6-IP correct
                   yes        no
P0 correct   yes   226        28
             no      8       772
```

Thus:

- P6-IP-only correct = 8;
- P0-only correct = 28;
- paired difference = −1.934 percentage points;
- exact McNemar p = 0.001193.

### 4.4 P6-IP: held-out schemas

| Metric | P0 | P6-IP |
|---|---:|---:|
| Correct | 60/254 | 55/254 |
| Accuracy | 23.622% | 21.654% |
| Mean cost | 0.26941 | 0.34795 |
| P95 latency | 7.367 s | 24.845 s |

Paired outcome counts:

```text
                    P6-IP correct
                   yes        no
P0 correct   yes    51         9
             no      4       190
```

The paired difference is −1.969 percentage points; exact McNemar p=0.266846.

The historical holdout execution is retained as locked observational corroboration. It is **not** treated as a fully prospective confirmatory experiment because holdout cases were executed before the entire development partition had been aggregated and frozen. No holdout outcome was used for tuning, and the development result alone triggers the stop rule.

### 4.5 The decisive result: harm versus rescue

| Partition | Eligible | P0-correct eligible | P0-wrong eligible | Harm | Rescue | Harm rate | Rescue rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 | **33.87%** | **0.75%** |
| Holdout | 91 | 16 | 75 | 5 | 1 | **31.25%** | **1.33%** |

### The key asymmetry

```text
Development intervention cases

P0-correct cases exposed to intervention
████████████████████████████████  62
                 │
                 └── harmed: 21  (33.87%)

P0-wrong cases exposed to intervention
████████████████████████████████████████████████████████████████ 268
                 │
                 └── rescued: 2   (0.75%)
```

The net intervention effect is therefore:

**2 rescues − 21 harms = −19 correctness-changing cases.**

The same directional asymmetry appears on held-out schemas.

### 4.6 Why the verification gate was insufficient

P6-IP rejected 173 challenger interventions on development and 52 on holdout, so incumbent preservation was genuinely implemented rather than merely described.

However, among accepted replacements, the gate still admitted harmful replacements. In development, 35 of 157 replacements were P0-correct incumbents, meaning **22.29% of replacements were harmful**.

This does not imply that verification is useless. It implies:

```text
SQL validity
      ≠
SQL executability
      ≠
structural consistency
      ≠
semantic correctness
      ≠
safe replacement authorization
```

That is the mechanism boundary exposed by the experiment.

### 4.7 Cost consequence

P6-IP is also more expensive because intervention requires additional execution:

- development: +25.8% mean cost versus P0;
- holdout: +29.2% mean cost versus P0.

Thus the challenger does not trade additional computation for a favorable reliability improvement. It spends more while reducing aggregate correctness.

---

## 5. Scientific Interpretation

### 5.1 What the experiment establishes

The strongest supported statement is:

> **Under the tested Spider cross-schema setting, decision-time evidence combined with executable and structural verification did not provide a sufficiently favorable harm–rescue trade-off for incumbent replacement.**

This is a conditional empirical result.

### 5.2 What it does not establish

The experiment does not establish that:

- no stronger verifier could work;
- no larger model could work;
- no enterprise benchmark could produce a different result;
- evidence-aware intervention is universally unsafe;
- adaptive execution is impossible;
- replacement can never be made reliable.

The correct conclusion is a **mechanism boundary**, not a universal impossibility theorem.

### 5.3 Why the negative result is useful

A positive routing result would have shown that one tested policy worked better. The negative P6-IP result answers a more diagnostic question:

> **Why is evidence-conditioned intervention not automatically safe?**

The answer supported by the data is that the evidence used by the selector and the verification gate is not sufficiently discriminative between:

- “incumbent is wrong and should be replaced,” and
- “incumbent is correct but exhibits evidence that looks risky.”

The experiment therefore distinguishes **risk evidence** from **replacement evidence**.

---

## 6. Defensibility Layer

The Defensibility Layer is deliberately orthogonal to the primary accuracy claim.

```text
QUESTION
   ↓
ANALYTICAL EXECUTION
   ↓
EVIDENCE + PROVENANCE
   ↓
POLICY / RISK DECISION
   ↓
VERIFICATION + AUTHORIZATION
   ↓
OUTCOME
   ↓
DEFENSIBILITY RECORD
```

Each decision should make it possible to answer:

1. What did the agent decide?
2. What evidence did it use?
3. Which policy/risk rule caused the action?
4. Which verification/authorization controls were applied?
5. What outcome, cost and accountability evidence was recorded?

This aligns with current enterprise reliability thinking: Gartner describes system-level guardrails and monitoring for agent reliability [25], Defensible AI and AgentOps as emerging enterprise architecture responsibilities [26], AI evaluation/observability as necessary for repeatable reliability measurement [27], and the need to instrument agent components so that what happened and what triggered an action can be reconstructed [28].

The layer does **not** establish legal compliance, complete governance, human-factors explainability or production readiness.

---

## 7. Limitations and Reviewer Attacks

### 7.1 P0 is weak

P0 achieves only 24.565% on development with `llama3.2:1b`. A reviewer can argue that the replacement behavior may differ with a stronger incumbent.

That criticism is valid. The result is therefore not an impossibility theorem. The paired harm/rescue result remains informative because it measures what the challenger does to cases that the incumbent gets right and wrong.

### 7.2 Verification is intentionally weak

The gate does not prove semantic equivalence. Stronger verifiers exist [1,2]. Therefore the paper claims only that the **tested gate** was insufficient.

### 7.3 Spider is not an enterprise production benchmark

Spider provides cross-schema Text-to-SQL evaluation, not real enterprise authorization, business definitions, privacy controls, workflow ownership or production distributions. Enterprise claims are consequently limited to an enterprise-motivated analytical execution methodology.

### 7.4 Holdout ordering deviation

The historical P6 workflow executed holdout cases before complete development aggregation/freeze. This is explicitly disclosed and prevents the holdout from being called fully prospective confirmation. No holdout outcome was used to tune the policy.

### 7.5 Implementation-specific failure

A reviewer may argue that the harm/rescue asymmetry is specific to the selector, model and verification implementation. This is a legitimate limitation. The paper consequently calls the result a **tested mechanism boundary**, not a universal impossibility result.

### 7.6 Literature coverage

The supplied corpus contains 53 links as provided, while the repository audit reports 54 unique arXiv IDs after removing one duplicate. Because not every supplied item was fully text-verified, the paper cites the directly verified and most constraining references for specific claims rather than falsely implying exhaustive full-text review of every item.

---

## 8. Conclusion

Project 1 does not end with a better router. It ends with a better-defined scientific boundary.

The central empirical finding is:

> **Correctness prediction, intervention eligibility and replacement authorization are different decisions.**

In the tested setting, intermediate evidence plus low-cost executable/structural verification was not sufficient for safe incumbent replacement. P6-IP harmed correct incumbents substantially more often than it rescued incorrect ones, increased cost, and reduced aggregate accuracy.

The result therefore rejects a simplistic progression of:

```text
more evidence → more confidence → replace incumbent
```

and replaces it with:

```text
more evidence
      ↓
better risk assessment?
      ↓
worth investigating?
      ↓
strong enough to authorize replacement?
      ↓
ONLY IF YES: replace
```

This distinction provides a concrete research boundary for future work. It also motivates Project 2: rather than immediately creating another router, build an evaluation and observability methodology capable of measuring the gap between predictive evidence, actionable evidence and evidence sufficient for consequential action.

---

## 9. Project 1 → Project 2

```text
PROJECT 1
Can an analytical agent act safely and efficiently?
             │
             ▼
NEGATIVE BOUNDARY
Evidence can be predictive without being safe authorization.
             │
             ▼
PROJECT 2
Can we measure, attribute and monitor that boundary?
             │
             ▼
PROJECT 3
Can consequential business optimization operate under
measured reliability, uncertainty, cost and action-risk constraints?
```

The Project 1 result is therefore an empirical input to the next research problem, not an algorithm to be rescued by further P7/P8 iteration.

---

# References

## Main scientific references

1. Richardson, R. (2026). **What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study.** arXiv:2607.06799. https://arxiv.org/abs/2607.06799
2. Shukla, N. K., Panda, D., Bhaduri, S., Banerjee, A., & Krishnamurthy, V. (2026). **TraceSQL: Traceable Answerability Estimation for Reference-Free Text-to-SQL Verification.** arXiv:2608.17795. https://arxiv.org/abs/2608.17795
3. Maleki, S. E., Pourreza, M., & Rafiei, D. (2026). **Confidence Estimation for Text-to-SQL in Large Language Models.** AAAI 2026, 40(38), 32474–32482. DOI: 10.1609/aaai.v40i38.40523.
4. Hussain, Z., & Nielbo, K. (2026). **The Coverage Illusion: From Pre-retrieval Routing Failure to Post-retrieval Cascades in a Production RAG System.** arXiv:2605.27220. https://arxiv.org/abs/2605.27220
5. Liskowski, P., Zhao, F., Han, B., Datta, A., & Tsirogiannis, D. (2026). **Compositional Online Learning for Semantic Data Processing Systems.** arXiv:2608.27244. https://arxiv.org/abs/2608.27244
6. Chen, K., Chen, Y., Koudas, N., & Yu, X. (2025). **Reliable Text-to-SQL with Adaptive Abstention.** Proceedings of the ACM on Management of Data, 3(1), Article 69. DOI: 10.1145/3709719.
7. Pillai, A. S. (2026). **GROUND: Reducing Hallucinations in LLM-Based Enterprise Analytics Through Governed Semantic Definitions.** arXiv:2608.26157. https://arxiv.org/abs/2608.26157
8. Sullutrone, G., Sala, L., Aftar, S., Koutrika, G., & Bergamaschi, S. (2026). **ABISS: Evaluating Text-to-SQL Systems Through Agent Interaction.** arXiv:2607.23340. https://arxiv.org/abs/2607.23340
9. **Agentic-SQL Revisited.** arXiv:2608.15389. https://arxiv.org/abs/2608.15389
10. **ACTS-SQL.** arXiv:2608.15145. https://arxiv.org/abs/2608.15145
11. **ZAS-SQL: Failure-derived rule distillation and early stopping.** arXiv:2606.08245. https://arxiv.org/abs/2606.08245
12. **TIDE-Bench.** arXiv:2608.29543. https://arxiv.org/abs/2608.29543
13. Singh, G., Kavehzadeh, P., Xia, J., Fu, X.-Y., Tremblay, J. B., Laskar, M. T. R., Lum, V., & Bhushan TN, S. (2026). **Beyond Text-to-SQL: An Agentic LLM System for Governed Enterprise Analytics APIs.** arXiv:2605.21027. https://arxiv.org/abs/2605.21027
14. Fei, Y., Jiang, Y., Yang, Y., & Xiao, X. (2026). **Benchmarking Text-to-SQL under Role-Based Access Control.** arXiv:2607.22115. https://arxiv.org/abs/2607.22115
15. **Beyond the Harness: End-to-End Optimization of Context Artifacts for Enterprise Text-to-SQL.** arXiv:2608.22830. https://arxiv.org/abs/2608.22830
16. **Disentangling Structure and Semantics.** arXiv:2608.20356. https://arxiv.org/abs/2608.20356
17. **Structure then Query / AnnoIndex.** arXiv:2608.13384. https://arxiv.org/abs/2608.13384
18. **DBLifeBench: Database Lifecycle Benchmark.** arXiv:2608.03794. https://arxiv.org/abs/2608.03794
19. **SQuaD-SQL: Efficient Text-to-SQL with Small Models.** arXiv:2607.08161. https://arxiv.org/abs/2607.08161
20. **TAHOE: Experience-driven hint optimization.** arXiv:2606.12387. https://arxiv.org/abs/2606.12387
21. **EnterpriseMem-Bench: Multi-turn enterprise Text-to-SQL memory.** arXiv:2605.26394. https://arxiv.org/abs/2605.26394
22. **DAB: Realistic enterprise data-agent benchmark.** arXiv:2603.20576. https://arxiv.org/abs/2603.20576
23. **BUDDY: Budget-driven dynamic computation depth.** arXiv:2606.09514. https://arxiv.org/abs/2606.09514
24. **Conditional Experience Transfer.** arXiv:2608.26730. https://arxiv.org/abs/2608.26730

## Gartner industry-context references

25. Gartner. (2026). **From Demo to Production: Closing the AI Agent Reliability Gap.** Published 8 May 2026. https://www.gartner.com/en/documents/7832217
26. Gartner. (2026). **Analyst Take: Designate a Defensible AI Architect Now.** Published 20 May 2026. https://www.gartner.com/en/documents/7887777
27. Gartner. (2026). **Market Guide for AI Evaluation and Observability Platforms.** Published 2 February 2026. https://www.gartner.com/en/documents/7387730
28. Gartner. (2026). **Engineering Trust: The New Hard Skill Essential for Leading AI.** Published 7 July 2026. https://www.gartner.com/en/documents/8102697
29. Gartner. (2026). **Use This Framework to Evaluate AI Agents.** Published 26 June 2026. https://www.gartner.com/en/documents/8061133
30. Gartner. (2026). **Observability Is a Must for Custom AI Agents and Multiagent Systems.** Published 17 August 2026. https://www.gartner.com/en/documents/8271421

> **Gartner citation rule:** Gartner references are included only to establish current industry relevance around reliability, defensibility, evaluation and observability. They are not used to establish academic novelty.

---

## Appendix A — Literature Corpus Map

The supplied literature review was organized into the following 53-link research structure. The manuscript cites the directly verified works that support specific claims rather than attaching every corpus item mechanically to unrelated sentences.

```text
53-LINK LITERATURE THREAT MODEL
│
├── A. Adaptive agents / tool use
│   ├── adaptive tool invocation
│   ├── MeCo / AdaTIR
│   ├── INTENT / budget-constrained agents
│   └── model-adaptive tool necessity
│
├── B. Routing / cascading
│   ├── unified routing and cascading
│   ├── streaming model cascades
│   ├── post-retrieval cascades
│   └── cost-aware model selection
│
├── C. Text-to-SQL generation
│   ├── agentic SQL
│   ├── schema/context optimization
│   ├── structure-first methods
│   └── execution-guided correction
│
├── D. Verification / confidence
│   ├── selective prediction
│   ├── TraceSQL
│   ├── confidence estimation
│   ├── execution/structural checks
│   └── learned verification
│
├── E. Reliability / interaction
│   ├── adaptive abstention
│   ├── ambiguity / unanswerability
│   ├── interactive Text-to-SQL
│   └── multi-turn degradation
│
├── F. Enterprise analytics
│   ├── governed semantic layers
│   ├── governed analytics APIs
│   ├── enterprise context artifacts
│   └── enterprise data-agent benchmarks
│
└── G. Security / defensibility
    ├── RBAC Text-to-SQL
    ├── deterministic safety boundaries
    ├── tool/action controls
    └── evaluation / observability
```

The literature audit explicitly found that the generic formulation “a sequential policy chooses tools/actions under a cost or reliability constraint” is already populated by prior work. The defensible gap is therefore the **empirical distinction between prediction, intervention and replacement authorization under incumbent asymmetry**.

---

## Appendix B — Reviewer Quick-Check

| Reviewer question | Manuscript answer |
|---|---|
| Is the RQ precise? | Yes; it distinguishes intervention from replacement. |
| Is adaptive routing claimed as novel? | No. |
| Is the literature gap generic? | No; it is an asymmetric replacement-authority gap. |
| Is P0 weak? | Yes; explicitly disclosed. |
| Is verification weak? | Yes; explicitly disclosed as a limitation and mechanism boundary. |
| Does Spider prove enterprise readiness? | No. |
| Is P6 failure universal? | No; it is conditional on the tested mechanism/model/benchmark. |
| Are comparisons paired? | Yes; exact McNemar for correctness, bootstrap for continuous differences. |
| Is the holdout deviation hidden? | No; explicitly disclosed. |
| Are Gartner reports used as novelty evidence? | No; industry-context only. |
| Why is the negative result useful? | It separates prediction, intervention and replacement authorization and quantifies harm/rescue asymmetry. |

---

## Appendix C — Locked Evidence Provenance

- P6-IP controlled inference run: `34252265013`
- Frozen P0–P5 source run: `34206500727`
- P0 comparator repair workflow: `34281611836`
- Corrected P6-IP analysis workflow: `34283127475`
- Official Spider evaluator commit: `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- P6-IP implementation branch: `research/p6-ip-defensibility`
- Defensibility design: `docs/PROJECT1_DEFENSIBILITY_LAYER.md`
- P6-IP result record: `docs/PROJECT1_P6_IP_RESULTS.md`

---

## Appendix D — Claim Discipline

The following claims are intentionally prohibited unless new evidence is produced:

- adaptive routing is novel;
- evidence-dependent execution is universally optimal;
- executable SQL is a reliable correctness verifier;
- incumbent-preserving intervention is solved;
- the method guarantees 90/95/97/99% reliability;
- Spider demonstrates production enterprise readiness;
- the result proves no stronger verifier could work;
- the literature contains no prior adaptive/cascade/verification methods.

The supported conclusion remains empirical and conditional on the tested setting.
