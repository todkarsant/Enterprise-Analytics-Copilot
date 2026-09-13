# When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents

**Project 1 — Enterprise Analytics Copilot**  
**Manuscript status:** Submission-ready research draft; empirical claims locked to executed evidence.  
**Target format:** arXiv-compatible preprint / Nature-style initial manuscript structure.  
**Branch:** `research/paper-lit-integration`

> **Submission baseline provenance:** The manuscript and its supporting repository state are anchored to the immutable Git commit `5e75dd57816ed6648f4657a9fb1c8654a007b744`. Experimental source runs, evaluator versions, corrected artifacts, and analysis-repair commits are documented separately below and in the repository research records.

## Abstract

Enterprise analytical agents increasingly combine retrieval, SQL generation, execution, verification, repair, clarification and escalation. A natural strategy is to use intermediate evidence to decide whether additional computation is warranted. A harder question is whether the same evidence is sufficiently trustworthy to authorize replacing an incumbent answer that may already be correct. This study separates three decisions that are often conflated: **correctness prediction, intervention eligibility, and replacement authorization**. We evaluate fixed, query-only and post-evidence policies (P0–P5), perform mechanism forensics (P5R), and then test an incumbent-preserving challenger (P6-IP) that begins from a frozen P0 answer, uses decision-time evidence to trigger intervention, and replaces the incumbent only after SQL validity, execution and structural verification checks. Correctness is evaluated only post hoc with the pinned official Spider evaluator.

Across the 1,034-case evaluation artifact, P0 is correct on 254 cases (24.565%) and P6-IP on 234 cases (22.631%), a paired difference of −1.934 percentage points (exact McNemar p=0.001193). Among development intervention-eligible cases, P6-IP harms 21 of 62 P0-correct incumbents (33.87%) while rescuing only 2 of 268 P0-wrong incumbents (0.75%); mean cost is approximately 25.8% higher than P0. On the 254 held-out-schema cases, the same directional pattern appears: 31.25% harm versus 1.33% rescue among eligible cases, with approximately 29.2% higher mean cost. The historical holdout execution preceded complete development aggregation and is therefore reported as locked observational corroboration rather than a fully prospective confirmatory test.

The results do not establish that adaptive intervention or verification is impossible. They expose a narrower mechanism boundary: **evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement**. Recent work on agentic AI, trustworthy decision-making and stronger Text-to-SQL verification reinforces why autonomy, verifiability and safety should not be collapsed into a single capability measure [31–33]. Work on AI auditing further shows that evaluation evidence is not equivalent to accountability unless audit design, methodology and institutional context support consequential follow-through [34]. Project 1 therefore adds a Defensibility Layer that preserves decision-time evidence, provenance, policy rationale, verification, authorization hooks, outcome, cost and reproducibility separately from post-hoc correctness labels. The resulting contribution is an empirical boundary study of incumbent replacement authority and an auditability-oriented research design, not a claim of universal routing optimality, formal safety, legal compliance, or production readiness.

## 1. Introduction

```text
QUESTION
   │
   ▼
EVIDENCE
   │
   ▼
RISK / POLICY
   │
   ▼
KEEP ────────────────► INCUMBENT
   │
   ▼
INTERVENE
   │
   ▼
CHALLENGER
   │
   ▼
VERIFY
   │
   ├── FAIL ─────────► PRESERVE INCUMBENT
   │
   └── PASS ─────────► REPLACE
```

Modern LLM-based analytical systems make sequential decisions. A system may retrieve schema information, generate SQL, execute it, inspect errors or results, verify structural properties, repair the query, ask for clarification, or escalate to a more capable agent. Recent reviews describe tool use, reflection, planning and autonomous action as established agentic design patterns [31]. Trustworthy-AI work likewise emphasizes that dependable decision-making requires verifiability, robustness, safety and explicit constraints rather than predictive performance alone [32]. Research on Text-to-SQL verification demonstrates that verification can itself involve substantially richer multi-stage mechanisms than simple execution or structural checks [33].

The scientific question is therefore not whether an analytical agent can adapt. It is whether **evidence that is useful for deciding to investigate a case is also strong enough to authorize replacing an incumbent answer**.

### Research question

> **When an analytical agent obtains intermediate evidence suggesting that its incumbent answer may be incorrect, what evidence is sufficient to justify additional computation, and what evidence is sufficient to justify replacing the incumbent without unacceptable reliability loss?**

The experimental version is narrower:

> **Under cross-schema Text-to-SQL workloads, does an evidence-triggered incumbent-preserving intervention policy using executable and structural verification improve the harm–rescue–cost trade-off relative to a frozen incumbent analytical policy?**

### What this paper does not claim

This paper does **not** claim that it invented:

- abstention;
- AI auditing or accountability;
- enterprise semantic governance;
- agentic Text-to-SQL.

Those are established areas in the supplied and directly verified literature [1–24,31–34].

Instead, the paper makes a narrower empirical contribution: it **separates prediction, intervention and replacement authorization, quantifies their asymmetric consequences, and adds an auditability-oriented evidence layer for reconstructing those decisions**.

## 2. Literature Threat Model

### 2.1 Why the literature was treated adversarially

The supplied corpus contains 53 paper links as provided for this research review; the repository audit reports 54 unique arXiv identifiers after removing one duplicate (`2608.13384`). The audit also records that not every supplied item was fully text-verified. Accordingly, this manuscript does not claim “53 papers deeply read” or “54 papers exhaustively verified.” Instead, the corpus is used as a **novelty threat model**, while claims are supported by the directly verified references listed below.

The literature clusters into the following families:

| Family | Established capability | Consequence for Project 1 |
|---|---|---|
| Interactive Text-to-SQL | Resolve ambiguity/unanswerability through interaction. | Evidence can indicate uncertainty without uniquely determining replacement. |
| Multi-turn/context optimization | Improve analytical context using memory and historical artifacts. | Context construction is another established axis. |
| Trustworthy decision-making | Use explicit constraints, verifiability, robustness and safety to support dependable decisions. | Decision evidence and control boundaries should not be conflated with model capability. |
| AI auditing/accountability | Audit effectiveness depends on methodology and institutional context, not logging alone. | Evaluation evidence and accountability must remain distinct. |

### 2.2 The closest novelty threats

**Agentic systems.** Reviews of agentic AI identify tool use, reflection, planning, ReAct-style interaction and autonomous decision-making as established patterns [31]. Project 1 therefore does not claim novelty for an agent simply acting sequentially or selecting tools.

**Trustworthy decision-making.** Song and Zhang's review frames trustworthy AI around verifiable, robust and safe decision-making under explicit physical knowledge and constraints [32]. Although their domain is physics-informed control, the principle is relevant here: explicit constraints and interpretable decision pathways matter when a learned system acts consequentially. Project 1 borrows that principle only at the framing level; it does not claim physics-informed guarantees.

**Text-to-SQL verification.** G²SQL demonstrates a substantially richer verification architecture combining a learning-based SQL-plan feedback loop with a Reviewer–Observer mechanism for generation, validation and revision [33]. This establishes an important threat to any claim that SQL execution or simple structural checks constitute a novel verifier.

**AI auditing and accountability.** Birhane et al. caution that conducting an AI audit does not by itself produce accountability; audit design, methodology, stakeholders and institutional context influence whether audit findings translate into accountability outcomes [34]. Project 1 therefore treats its provenance and decision records as **auditability-supporting evidence**, not as proof of accountability or compliance.

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

Project 1 tests whether a signal useful for Level 1/2 is sufficient for Level 3. The AI-auditing literature adds a complementary Level 4: **can the consequential decision later be reconstructed and challenged from preserved evidence?** [34]

The paper's central proposition is therefore:

> **Evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.**

That proposition is falsifiable because replacement creates observable paired outcomes: rescue, harm, preservation of a correct incumbent, or preservation of a wrong incumbent.

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
      ▼
P6-IP INCUMBENT-PRESERVING CHALLENGER
      │
      ▼
HARM / RESCUE TEST
      │
      ▼
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
              evidence / risk
                 ┌────┴────┐
               KEEP     INTERVENE
                          │
                          ▼
                     challenger
                          │
                          ▼
                     verification
                    ┌─────┴─────┐
                  REJECT      ACCEPT
                    │             │
                    ▼             ▼
                preserve       replace
```

The gate checks:

1. SQL validity;
2. successful execution;
3. structural consistency with detected question requirements.

It does **not** establish semantic equivalence between incumbent and challenger results. Recent G²SQL work demonstrates that substantially stronger verification architectures are possible, so the present gate should be understood as a deliberately constrained baseline [33].

### 3.6 Decision-time versus post-hoc separation

```text
DECISION TIME                         POST HOC
─────────────                         ────────
Question                              Gold SQL
Evidence                              Official evaluator
Risk reason                           Correctness label
KEEP / INTERVENE                      Statistical analysis
Challenger SQL
Verification result
```

This separation prevents the evaluator from becoming an oracle inside the policy and supports later reconstruction of consequential decisions [34].

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
- evidence provenance completeness;
- auditability/reproducibility fields.

### 3.8 Statistical tests

Because the same cases are evaluated by both policies, paired correctness comparisons use exact two-sided McNemar tests. Continuous paired differences use bootstrap confidence intervals. Wilson intervals are used for intervention harm/rescue proportions.

The 90/95/97/99% reliability targets are retained as predefined diagnostic targets. They are not interpreted as attainable production guarantees because the tested P0 itself is far below those values.

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

Diagnostic evidence models found predictive signal in evidence features, but the selector was not sufficiently aligned with P0 correctness to safely authorize replacement. For transparency, the reason-only diagnostic model achieved development 5-fold CV AUC ≈0.566, while the richer `reason + row + col` diagnostic achieved development CV AUC ≈0.696 and holdout AUC ≈0.791; these are post-hoc diagnostic analyses, not policy inputs or claims of calibrated probability.

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

- development: approximately +25.8% mean cost versus P0;
- holdout: approximately +29.2% mean cost versus P0.

Thus the challenger does not trade additional computation for a favorable reliability improvement. It spends more while reducing aggregate correctness.

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

The correct conclusion is a **mechanism boundary**, not a universal impossibility theorem. G²SQL is particularly relevant here because it demonstrates a stronger multi-stage verification design than the constrained gate tested in this study [33].

### 5.3 Why the negative result is useful

A positive routing result would have shown that one tested policy worked better. The negative P6-IP result answers a more diagnostic question:

> **Why is evidence-conditioned intervention not automatically safe?**

The observed harm–rescue asymmetry is **consistent with the tested evidence features and verification gate failing to reliably discriminate between**:

- “incumbent is wrong and should be replaced,” and
- “incumbent is correct but exhibits evidence that looks risky.”

The experiment therefore distinguishes **risk evidence** from **replacement evidence**.

### 5.4 From evaluation to auditability

The empirical result also clarifies a separate layer of defensibility. Official execution accuracy evaluates correctness under the benchmark protocol. It does not, by itself, show that a consequential decision can later be reconstructed, challenged, assigned to a policy, or connected to evidence. Birhane et al. emphasize that effective auditing depends on audit design, methodology and institutional context rather than on the existence of an audit record alone [34]. Accordingly, Project 1 treats its provenance, policy rationale and decision traces as **auditability-supporting evidence** rather than as proof of accountability.

## 6. Defensibility Layer

The Defensibility Layer is deliberately orthogonal to the primary accuracy claim. It is an evidence/provenance and control-observability layer, not a claim of legal compliance or complete enterprise governance.

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

This layer is informed by two complementary strands of literature. Trustworthy-computing work emphasizes explicit constraints and verifiable decision pathways [32], while AI-auditing research cautions that evidence and audit procedures do not automatically create institutional accountability [34]. Project 1 therefore preserves the evidence needed for reconstruction while explicitly stopping short of claiming accountability itself.

Current enterprise reliability thinking also supports system-level guardrails, monitoring, evaluation and observability [29–34]. Those references establish industry relevance rather than academic novelty.

### 6.1 Auditability versus accountability

```text
Auditability
    = Can we reconstruct what evidence and policy caused the action?

Accountability
    = Can evidence support challenge, ownership,
      remediation and consequential oversight?
```

Project 1 directly evaluates the first, instruments the second, and does **not** claim to have experimentally established the third.

### 6.2 Decision record contract

The intended research record contains case identity, schema, policy/code commit, model/provider/version, dataset/evaluator manifest, incumbent SQL, pre-intervention evidence and provenance, selector rationale, KEEP/INTERVENE decision, challenger SQL, verification checks, replacement/preservation outcome, harm/rescue class, abstention/runtime status, latency, token/call/cost measures, errors, timestamp and correlation identifier.

Gold/evaluator correctness remains a post-hoc field and is not available to the decision-time policy. This separation prevents oracle leakage while preserving the evidence needed for retrospective audit and reproducibility [34].

### 6.3 Control hooks

The Defensibility Layer exposes explicit control points for:

```text
authorization
     ↓
data-access policy
     ↓
tool/action allow-list
     ↓
SQL safety
     ↓
budget / timeout
     ↓
verification
     ↓
auditable outcome
```

Spider does not supply realistic organizational authorization metadata, so the experiment does not claim to validate RBAC/ABAC or legal compliance. Those require a separate benchmark and control study [14].

## 7. Limitations and Reviewer Attacks

### 7.1 P0 is weak

P0 achieves only 24.565% on the 1,034-case evaluation artifact with `llama3.2:1b`. A reviewer can argue that replacement behavior may differ with a stronger incumbent.

That criticism is valid. The result is therefore not an impossibility theorem. The paired harm/rescue result remains informative because it measures what the challenger does to cases that the incumbent gets right and wrong.

### 7.2 Verification is intentionally weak

The gate does not prove semantic equivalence. Stronger verification systems exist, including the multi-stage G²SQL architecture [33]. The paper therefore claims only that the **tested gate** was insufficient. It does not claim that stronger verification cannot support safe replacement.

### 7.3 Domain transfer from trustworthy-computing literature is limited

Song and Zhang address physics-informed AI for safety-critical physical decision-making and control [32]. Project 1 operates in analytical Text-to-SQL. The transferable point is the importance of explicit constraints and verifiability, not the physical-law mechanism or its safety guarantees.

### 7.4 AI auditing does not equal accountability

Birhane et al. explicitly distinguish audit practice from effective accountability [34]. Project 1's provenance and trace records should therefore be described as auditability infrastructure. They do not prove institutional accountability, human oversight, legal compliance, or effective remediation.

### 7.5 Spider is not an enterprise production benchmark

Spider provides cross-schema Text-to-SQL evaluation, not real enterprise authorization, business definitions, privacy controls, workflow ownership or production distributions. Enterprise claims are consequently limited to an enterprise-motivated analytical execution methodology.

### 7.6 Holdout ordering deviation

The historical P6 workflow executed holdout cases before complete development aggregation/freeze. This is explicitly disclosed and prevents the holdout from being called fully prospective confirmation. No holdout outcome was used to tune the policy.

### 7.7 Implementation-specific failure

A reviewer may argue that the harm/rescue asymmetry is specific to the selector, model and verification implementation. This is a legitimate limitation. The paper consequently calls the result a **tested mechanism boundary**, not a universal impossibility result.

### 7.8 Literature coverage

The supplied corpus contains 53 links as provided, while the repository audit reports 54 unique arXiv IDs after removing one duplicate. Because not every supplied item was fully text-verified, the paper cites the directly verified and most constraining references for specific claims rather than falsely implying exhaustive full-text review of every item.

## 8. Conclusion

Project 1 does not end with a better router. It ends with a better-defined scientific boundary.

Across the tested Spider cross-schema workload, the evidence-triggered incumbent-preserving policy did not improve reliability or cost. Relative to the frozen P0 incumbent, P6-IP reduced accuracy by approximately 1.93 percentage points on the full evaluation artifact and increased mean cost by approximately 25.8%. More importantly, the intervention analysis exposed a strong asymmetry: on development cases eligible for intervention, 33.87% of P0-correct incumbents were harmed while only 0.75% of P0-wrong incumbents were rescued. The held-out-schema partition showed the same directional pattern, with 31.25% harm versus 1.33% rescue among eligible cases. The historical holdout is treated only as observational corroboration because of its execution ordering.

These results support a narrow conclusion rather than a universal theorem. **Decision-time evidence can be sufficient to justify investigation without being sufficient to authorize replacement.** Executability and structural consistency are useful control signals, but in this tested configuration they did not provide adequate protection against harmful replacement. Stronger verification architectures remain a live alternative and are explicitly outside the claim boundary [33].

The study also establishes a separation between three technical decisions—prediction, intervention and replacement authorization—and a separate accountability-oriented evidence question: whether the decision can later be reconstructed and examined. The Defensibility Layer operationalizes that fourth concern through provenance, policy rationale, verification, authorization hooks, outcome and reproducibility records, while the AI-auditing literature provides the caution that such records support auditability rather than automatically creating accountability [34].

The practical research consequence is therefore not “add another router.” It is to measure, attribute and monitor the gap between **predictive evidence, actionable evidence, replacement-authorizing evidence, and auditable evidence**. This directly motivates Project 2: a production-oriented LLM evaluation and observability platform designed to quantify such boundaries rather than obscure them.

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
AUDITABILITY LAYER
Can we reconstruct and challenge the consequential decision?
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
25. Nisa, U., Shirazi, M., Saip, M. A., & Pozi, M. S. M. (2026). **Agentic AI: The age of reasoning—A review.** *Journal of Automation and Intelligence*, 5(1), 69–89. DOI: 10.1016/j.jai.2025.08.003.
26. Song, Y., & Zhang, A. (2026). **From black box to physically interpretable: Trustworthy computing for AI-driven decision-making and control.** *Journal of Automation and Intelligence*, 5(2), 91–111. DOI: 10.1016/j.jai.2025.09.003.
27. Li, X., You, J., Li, H., Peng, J., Chen, X., Guo, Z., Li, K., & Xu, T. (2026). **G²SQL: guided & guarded Text-to-SQL generation with two-stage verification.** *Expert Systems with Applications*, 311, 131276. DOI: 10.1016/j.eswa.2026.131276.
28. Birhane, A., Steed, R., Ojewale, V., Vecchione, B., & Raji, I. D. (2024). **AI auditing: The Broken Bus on the Road to AI Accountability.** arXiv:2401.14462. https://arxiv.org/abs/2401.14462

## Gartner industry-context references

29. Gartner. (2026). **From Demo to Production: Closing the AI Agent Reliability Gap.** Published 8 May 2026.
30. Gartner. (2026). **Analyst Take: Designate a Defensible AI Architect Now.** Published 20 May 2026.
31. Gartner. (2026). **Market Guide for AI Evaluation and Observability Platforms.** Published 2 February 2026.
32. Gartner. (2026). **Engineering Trust: The New Hard Skill Essential for Leading AI.** Published 7 July 2026.
33. Gartner. (2026). **Use This Framework to Evaluate AI Agents.** Published 26 June 2026.
34. Gartner. (2026). **Observability Is a Must for Custom AI Agents and Multiagent Systems.** Published 17 August 2026.

# Data Availability, Code Availability and Experimental Reproducibility

The public Spider benchmark and the research code required to reproduce the reported analyses are maintained in this repository. The submission manuscript baseline is identified by the immutable Git commit `5e75dd57816ed6648f4657a9fb1c8654a007b744`.

The primary experimental provenance is preserved through the repository's research records, including the frozen P0–P5 run, the P6-IP controlled run, the pinned official Spider evaluator, corrected post-hoc P0 case-level artifacts, and the analysis-repair outputs. No new LLM inference is required to reproduce the numerical conclusions reported here; the corrected P0 labels were recomputed post hoc from frozen P0 SQL outputs using the pinned evaluator, without an inference rerun.

The P6-IP controlled experiment was executed on GitHub Actions using local Ollama inference rather than paid/Azure inference. The development artifact contains 1,034 cases and the locked held-out-schema partition contains 254 cases. The historical ordering limitation of the holdout execution is documented in the Methods/Limitations sections and is not concealed by the availability statement.

Repository code, configuration, tests, manifests, raw result artifacts where committed or retained by the research workflow, and analysis scripts are intended to provide an auditable chain from implementation to reported result. External users should verify the referenced run IDs, commit hashes and artifact manifests against the repository state when reproducing the study.

# References and provenance note

Reference numbering in the current manuscript is intentionally constrained to the scientific references and Gartner industry-context references above. Gartner material is used only for industry-context relevance and not as evidence of academic novelty. The manuscript does not claim exhaustive full-text verification of every item in the original literature corpus.
