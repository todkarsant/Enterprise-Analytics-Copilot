# When Evidence Is Not Enough: Replacement Decisions in Analytical AI Agents

**Author:** Santosh S. Todkar  
**Affiliation:** *Author to complete the affiliation and full postal address required by JAI*  
**Corresponding author:** Santosh S. Todkar  
**E-mail:** *Author to supply*  

## Abstract

AI agents can retrieve evidence, generate and execute SQL, and invoke additional reasoning when an analytical task appears difficult. In enterprise analytics, however, detecting risk is not the same as knowing when an answer should be changed. This study examines whether evidence that justifies further investigation is also sufficient to authorize replacement of an existing answer.

We separate three decisions: predicting that an answer may be wrong, deciding whether additional computation is justified, and authorizing replacement. We evaluate frozen baseline policies, perform mechanism forensics, and test an incumbent-preserving policy that intervenes using decision-time evidence and replaces the incumbent only after SQL validity, execution, and structural checks.

On 1,034 cross-schema Text-to-SQL cases, the incumbent achieves approximately 24.6% execution accuracy, versus 22.6% for the tested replacement policy, while mean cost increases by approximately 25.8%. Among development cases selected for intervention, 33.87% of correct incumbent answers were harmed, whereas only 0.75% of incorrect incumbent answers were rescued. The held-out-schema partition shows the same directional pattern.

The result establishes a practical reliability boundary: **evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement**. The study therefore separates risk detection, intervention, replacement authorization, and auditability as distinct controls for analytical AI systems.

**Keywords:** Analytical agent; Text-to-SQL; Selective prediction; Verification; Auditability

## 1. Introduction

Modern analytical agents do more than generate answers. They retrieve schema information, generate SQL, execute tools, inspect errors or results, verify structural properties, repair queries, ask for clarification, or escalate to additional reasoning. These capabilities are established agentic design patterns rather than, by themselves, a research contribution [25]. Trustworthy-AI research likewise emphasizes verifiability, robustness, safety and explicit constraints when AI systems make consequential decisions [26]. Recent Text-to-SQL work demonstrates that verification can involve substantially richer multi-stage mechanisms than execution or simple structural checks [27].

The harder problem is **decision authority**. When an agent observes evidence suggesting that an answer may be wrong, should it merely investigate further, or should it be allowed to replace the answer it already has?

This paper separates three decisions:

```text
RISK
Is the current answer suspicious?
        ↓
INTERVENTION
Is additional computation justified?
        ↓
REPLACEMENT
Is the challenger strong enough to discard the incumbent?
        ↓
AUDITABILITY
Can the decision later be reconstructed and examined?
```

The central proposition is:

> **Evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.**

The experimental question is narrower:

> **Under a cross-schema Text-to-SQL workload, can an evidence-triggered incumbent-preserving policy improve the harm–rescue–cost trade-off relative to a frozen incumbent analytical policy?**

The paper does not claim novelty for agentic Text-to-SQL, abstention, adaptive routing, verification, AI auditing, or enterprise semantic governance. Those are established research areas [1–8,10–24,25–28]. The contribution is the empirical separation of prediction, intervention and replacement authorization; paired measurement of harm and rescue; and a defensibility-oriented evidence record for reconstructing consequential decisions.

## 2. Related Work and Adversarial Literature Positioning

### 2.1 Correctness prediction and verification

Correctness estimation for Text-to-SQL is already an active research problem. Maleki et al. study black-box and white-box confidence estimation and show that execution-based grounding can provide useful supplementary evidence [3]. Richardson reports that simple structural, execution and self-consistency signals have limited correctness-discrimination power relative to stronger reasoning-based verification, with cross-schema generalization remaining difficult [1]. TraceSQL likewise uses explicit diagnostic features for reference-free answerability estimation [2]. These results rule out presenting executability, structural checks, or traceability as novel correctness-verification mechanisms.

Reliable Text-to-SQL with Adaptive Abstention establishes abstention and human interaction as reliability controls, including statistical guarantees for schema-linking uncertainty [6]. Project 1 therefore does not claim to invent safe abstention or uncertainty-aware interaction.

G²SQL provides an especially important comparator because it uses a two-stage guided and guarded verification architecture with a Reviewer–Observer mechanism [27]. The verification gate tested in this paper is intentionally much weaker: SQL validity, execution, and selected structural consistency. A negative result for that gate must therefore not be interpreted as evidence that stronger verification is ineffective.

### 2.2 Adaptive computation and cascades

The literature already contains adaptive routing and cascading at several levels. The Coverage Illusion shows that the need for expensive augmentation may become visible only after retrieval and evaluates a cheapest-first post-retrieval cascade in a production RAG system [4]. Compositional Online Learning for Semantic Data Processing Systems makes execution-time decisions and includes semantic SQL cascade routing [5]. Agentic-SQL Revisited provides a published taxonomy and empirical analysis of Text-to-SQL autonomy levels [9]. ACTS-SQL uses tree-structured correction, backtracking, execution-based verification and clause-level diagnostics [10]. ZAS-SQL distils failure-derived rules and uses execution-guided early stopping [11]. TAHOE learns reusable hints from debugging and execution experience [20].

Accordingly, Project 1 does not claim novelty for “adaptive routing,” “post-evidence escalation,” “cost-aware computation,” “agentic SQL,” or “execution-guided correction.” Those are treated as prior-art constraints and, where relevant, baseline mechanisms.

### 2.3 Enterprise analytical reliability and governance

GROUND formalizes governed enterprise analytics around approved metrics, dimensions, joins, grain, filters, security and cost rules [7]. Beyond Text-to-SQL describes governed enterprise analytics APIs with permission validation and policy-aware orchestration [13]. RBAC-aware Text-to-SQL benchmarking demonstrates that unrestricted benchmark accuracy can conceal authorization failures [14]. DAB evaluates realistic data-agent workloads involving multiple databases, unstructured information and domain knowledge [22]. EnterpriseMem-Bench examines memory architectures for multi-turn enterprise Text-to-SQL [21], while ABISS studies ambiguous and unanswerable questions under interactive agent sessions [8]. These works establish that enterprise analytical reliability cannot be reduced to SQL syntax or single-turn execution accuracy.

Beyond the Harness shows that enterprise Text-to-SQL quality can depend strongly on the context artifacts supplied to the model [15]. Disentangling Structure and Semantics separates structural and semantic schema effects [16]. Structure then Query / AnnoIndex studies a different architecture in which structured annotations support cheaper filtering before more expensive semantic operations [17]. SQuaD-SQL studies efficient small-model Text-to-SQL [19]. DBLifeBench broadens evaluation toward database lifecycle behavior [18].

### 2.4 Auditability and trustworthy decision-making

Birhane et al. show that AI audit activity does not automatically translate into accountability; audit design, methodology and institutional context influence whether audit findings have consequential effect [28]. Project 1 therefore uses the term **auditability** deliberately: the Defensibility Layer preserves evidence needed to reconstruct a decision but does not claim legal compliance or institutional accountability.

Gartner's 2026 industry research similarly emphasizes system-level reliability, evaluation, observability, defensibility, challenge, transparency and accountability for AI agents [29–34]. These sources are used only as industry-context evidence, not as evidence of academic novelty.

### 2.5 The narrow gap tested here

The literature separately studies correctness prediction, intervention, routing, verification, abstention, agentic execution, enterprise governance and auditability. Project 1 asks whether **evidence useful for deciding to investigate is also strong enough to authorize replacement of an incumbent answer**.

This distinction creates an experimentally observable asymmetry. A replacement policy can:

1. rescue a wrong incumbent;
2. harm a correct incumbent;
3. preserve a correct incumbent; or
4. preserve a wrong incumbent.

The paper evaluates these outcomes directly rather than collapsing them into a single confidence or accuracy score.

## 3. Research Design

### 3.1 Falsification sequence

The study was designed as a staged falsification process rather than as an attempt to force a positive result.

```text
Literature audit
      ↓
Reject broad adaptive-routing novelty
      ↓
Frozen P0–P5 baselines
      ↓
P5 mechanism forensics (P5R)
      ↓
P6-IP incumbent-preserving challenger
      ↓
Harm / rescue analysis
      ↓
Stop algorithmic escalation
```

P0–P5 were frozen before the final challenger. P5R was used as mechanism forensics and did not alter the frozen baselines. P6-IP was explicitly defined as the final controlled challenger. The predefined stop rule was to stop further algorithmic escalation if incumbent harm remained materially larger than rescue without a favorable cost trade-off.

### 3.2 Benchmark and partitions

The Spider development artifact contains 1,034 cases. A schema-level split with seed 1729 assigns four schemas—`car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`—to a 254-case held-out-schema partition. The remaining 16 schemas form a 780-case development partition.

The 254 cases are therefore a partition of the 1,034-case artifact rather than an independent second dataset. Spider provides a controlled cross-schema Text-to-SQL setting; it does not establish production enterprise readiness, real authorization correctness, or organizational governance.

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
| Parent timeout | 150 s |
| Runtime chunks | 12 |
| Iterative model | Ollama `llama3.2:1b` |
| Paid/Azure inference | Not used |

Official Spider execution accuracy is the primary correctness metric. Custom row-set equality is treated only as a diagnostic. Runtime failures and timeouts remain in the denominator.

### 3.4 Policy ladder

```text
P0  Always-LLM incumbent
P1  Deterministic-only
P2  Static Hybrid
P3  Query-only Complexity Router
P4  Query-only Heuristic Confidence Router
P5  Post-Evidence Cascade
        ↓
P5R Mechanism Forensics
        ↓
P6-IP Incumbent-Preserving Challenger
```

P2 and P3 produced identical behavior under the implemented decision rule and are not interpreted as independent evidence of two distinct successful mechanisms. P4 is a deterministic heuristic rather than a calibrated confidence estimator.

### 3.5 P6-IP

P6-IP begins from the P0 incumbent rather than selecting a replacement from scratch.

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

The tested verification gate checks:

1. SQL validity;
2. successful execution;
3. structural consistency with detected question requirements.

It does not establish semantic equivalence between incumbent and challenger results. This limitation is explicit and is important when interpreting the negative result relative to stronger verification work [27].

### 3.6 Decision-time versus post-hoc evidence

Decision-time fields are kept separate from post-hoc gold/evaluator fields:

| Decision-time | Post-hoc |
|---|---|
| Question | Gold SQL |
| Evidence | Official execution result |
| Evidence provenance | Correctness label |
| Risk reason | Statistical comparison |
| KEEP / INTERVENE | Confidence intervals |
| Challenger SQL | Paired tests |
| Verification | Failure taxonomy |

This separation prevents the official evaluator from becoming an oracle inside the policy.

### 3.7 Primary and secondary metrics

Primary metrics are official execution accuracy, paired correctness, incumbent harm, rescue, intervention rate, mean cost and latency. Secondary metrics include replacement/rejection rates, model calls, input/output tokens, P50/P95/P99 latency, runtime failures, decision-trace completeness and evidence-provenance completeness.

Paired correctness differences use exact two-sided McNemar tests. Continuous paired differences use bootstrap confidence intervals. Wilson intervals are used for harm and rescue proportions. The 90%, 95%, 97% and 99% reliability targets are retained as diagnostic targets rather than production guarantees.

## 4. Results

### 4.1 Frozen P0–P5 baseline

| Policy | Correct / 1,034 | Accuracy |
|---|---:|---:|
| P0 | 254 | 24.565% |
| P1 | 0 | 0.000% |
| P2 | 256 | 24.758% |
| P3 | 256 | 24.758% |
| P4 | 20 | 1.934% |
| P5 | 123 | 11.896% |

P5 reduced mean cost by approximately 9.35% relative to P0, but with a large accuracy loss. P0 was correct while P5 was wrong on 158 cases; P5 rescued 27 cases where P0 was wrong. The exact paired McNemar p-value was approximately 1 × 10^-23.

The result does not support P5 as a reliability-improving replacement for P0. Its lower model-work footprint was accompanied by materially worse correctness and a substantially longer upper latency tail.

### 4.2 P5R mechanism forensics

P5R improved over P5 but did not recover P0. On the 1,034-case development artifact, P5R achieved 179/1,034 = 17.311% official accuracy. The paired difference versus P0 was −7.253 percentage points. P5R also increased cost relative to P5.

Diagnostic evidence features contained predictive signal, but the selector was not sufficiently aligned with incumbent correctness to authorize replacement safely. The diagnostic analysis is explicitly post-hoc and was not used to tune the held-out partition.

### 4.3 P6-IP primary result

On development, P6-IP achieved 234/1,034 = 22.631% official execution accuracy versus 254/1,034 = 24.565% for P0. The paired difference was −1.934 percentage points, with exact McNemar p = 0.001193. Mean cost increased from approximately 0.269 to 0.338, an increase of approximately 25.8%.

The paired correctness table was:

| Outcome | Cases |
|---|---:|
| Both correct | 226 |
| P0 correct, P6-IP wrong | 28 |
| P6-IP correct, P0 wrong | 8 |
| Both wrong | 772 |

Thus the challenger harmed more incumbent-correct cases than it rescued incumbent-wrong cases.

### 4.4 Harm–rescue intervention analysis

| Partition | Eligible interventions | P0-correct eligible | P0-wrong eligible | Harm | Rescue |
|---|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 |
| Held-out schemas | 91 | 16 | 75 | 5 | 1 |

For development, harm among P0-correct intervention-eligible cases was 21/62 = **33.87%**, while rescue among P0-wrong intervention-eligible cases was 2/268 = **0.75%**. Correctness-changing interventions were 23/330 = 6.97%, with a net intervention contribution of −19 cases.

For the held-out-schema partition, harm was 5/16 = **31.25%**, while rescue was 1/75 = **1.33%**. This is directional corroboration only because the historical holdout execution occurred before complete development aggregation and freeze. No holdout result was used for tuning, and the development result alone triggered the stop rule.

### 4.5 Reliability targets

P6-IP did not meet the predefined 90%, 95%, 97% or 99% diagnostic reliability targets on either partition. This is unsurprising given the low absolute accuracy of the frozen P0 incumbent and is not interpreted as a claim that those reliability levels are impossible in other systems.

### 4.6 Latency and cost

P6-IP increased mean cost by approximately 25.8% on development and approximately 29.2% on the held-out-schema partition. Development median latency was approximately 2.10 s for P6-IP versus 2.00 s for P0; development P95 latency was approximately 13.6 s versus 5.6 s. Holdout P95 latency was approximately 24.8 s for P6-IP versus 7.4 s for P0.

These tails matter because an intervention policy can appear acceptable at the median while imposing substantial operational delay on difficult cases.

## 5. Discussion

### 5.1 What the experiment establishes

The strongest supported statement is:

> **Under the tested Spider cross-schema setting, decision-time evidence combined with executable and structural verification did not provide a sufficiently favorable harm–rescue trade-off for incumbent replacement.**

In plain language:

> **The system could find reasons to look again, but those reasons were not reliable enough to justify throwing away the current answer.**

This is a conditional empirical result. It does not establish that stronger verifiers, larger models, different enterprise datasets, or other evidence policies would fail.

### 5.2 Why the negative result is scientifically useful

The failure is not simply “P6 is less accurate.” The paired intervention analysis identifies the mechanism failure more precisely. The policy was allowed to intervene in 330 development cases. Among cases where the incumbent was correct, the intervention caused harm much more often than it rescued cases where the incumbent was wrong.

This distinguishes three concepts that are often compressed into “confidence”:

1. **Risk detection:** evidence that the incumbent may be wrong.
2. **Intervention value:** evidence that additional computation is worth its cost.
3. **Replacement authorization:** evidence strong enough to discard the incumbent.

A signal can be useful for the first or second decision without being safe for the third.

### 5.3 Verification boundary

The tested verification gate was intentionally limited. It checked validity, execution and structural cues, but did not compare semantic result equivalence or use a strong independent reasoning verifier. Recent published work such as G²SQL demonstrates richer two-stage verification [27], while correctness-prediction work shows that stronger reasoning-based verification can outperform simple structural/execution signals [1,3]. Therefore, the present experiment should be interpreted as a negative result for **this tested class of incumbent-preserving verification**, not for verification in general.

### 5.4 Benchmark boundary

Spider is valuable for controlled cross-schema evaluation but is not an enterprise production benchmark. It lacks the organizational authorization, governed semantic definitions, production workload variability and institutional accountability required for a production enterprise claim. The enterprise relevance of Project 1 is therefore architectural and methodological: it studies a decision-authority problem that can arise in enterprise analytical systems, while using Spider as a controlled public test environment.

### 5.5 Model boundary

The final controlled experiments use local Ollama inference with `llama3.2:1b`. The model is intentionally documented rather than hidden. The result should not be generalized to frontier models. A stronger model could change both the incumbent quality and the value of verification, and therefore represents a future experimental dimension rather than a reason to reinterpret the present result.

### 5.6 Defensibility Layer

The negative correctness result does not eliminate the value of auditability. A benchmark evaluator answers:

> Was the final answer correct?

A defensibility record should additionally support:

> What did the system know when it acted?  
> What evidence triggered the action?  
> Which policy rule was applied?  
> Which verification and authorization controls were used?  
> What happened, and can the decision be reconstructed later?

The Defensibility Layer therefore preserves evidence provenance, policy rationale, verification, authorization hooks, outcomes, cost and reproducibility separately from post-hoc correctness labels. It does not prove legal compliance, institutional accountability, or production governance.

## 6. Threats to Validity

**Incumbent weakness.** P0 is only approximately 24.6% accurate. This limits absolute performance claims. The paired harm/rescue analysis remains informative because every policy sees the same cases.

**Small model.** The use of `llama3.2:1b` limits generalization to stronger models.

**Verification strength.** The gate is weaker than recent multi-stage verifiers. The result therefore bounds the tested mechanism rather than verification as a field.

**Benchmark transfer.** Spider is not an enterprise deployment benchmark.

**Holdout ordering.** The historical held-out-schema execution preceded complete development aggregation. It is therefore reported as locked observational corroboration rather than fully prospective confirmation.

**Post-hoc diagnostics.** Diagnostic models were used for mechanism understanding only. They did not become part of the P6-IP decision rule or tune the held-out partition.

**Multiple comparisons.** The primary P6-IP comparison is paired and prespecified. Additional analyses are treated as supporting diagnostics rather than independent discovery claims.

## 7. Reproducibility and Data Availability

The public Spider benchmark and research code required for the reported analyses are maintained in the repository. The official evaluator commit is pinned to `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`. P6-IP was executed in GitHub Actions with local Ollama inference; paid/Azure inference was not used.

The development artifact contains 1,034 cases and the locked held-out-schema partition contains 254 cases. Runtime traces, decision records, provenance manifests, statistical analysis scripts, tests and workflow definitions are retained in the repository or associated research artifacts where applicable.

The manuscript's research chain is anchored to the repository history rather than to a mutable benchmark result. Users reproducing the work should verify the cited commits, run identifiers, evaluator version and artifact manifests against the repository.

**Data availability:** The Spider dataset is publicly available from its original distribution. Project-specific derived traces and analysis artifacts are maintained with the repository subject to repository/artifact availability constraints.

## 8. Code Availability

Source code, evaluation scripts, policy implementations, tests, workflow definitions and analysis utilities are maintained in the project repository. The repository preserves the distinction between frozen baseline policies, challenger experiments, post-hoc evaluator analysis and the Defensibility Layer.

## 9. Funding

**Funding:** *Author verification required. If this work received no specific funding, replace this line with: “This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.”*

## 10. Declaration of Competing Interest

**Competing interests:** *Author verification required. If there are no financial or personal relationships that could have influenced this work, use: “The author declares no competing financial or personal interests that could have influenced this work.”*

## 11. Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

During preparation of this manuscript, the author used OpenAI ChatGPT to assist with language editing, structural revision and preparation of publication-oriented text. The author reviewed and edited the resulting material and takes full responsibility for the accuracy, integrity and final content of the manuscript.

## 12. Author Contributions

Santosh S. Todkar: Conceptualization; Methodology; Software; Investigation; Formal analysis; Validation; Data curation; Visualization; Writing – original draft; Writing – review & editing; Project administration.

## 13. Acknowledgements

The author thanks the open-source Spider benchmark and evaluation ecosystem and the maintainers of the tools used to reproduce the controlled experiments. No external scientific claim is attributed to these resources beyond their documented role in the experiment.

## References

[1] R. Richardson, “What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study,” arXiv:2607.06799, 2026.

[2] N. K. Shukla, D. Panda, S. Bhaduri, A. Banerjee, and V. Krishnamurthy, “TraceSQL: Traceable Answerability Estimation for Reference-Free Text-to-SQL Verification,” arXiv:2608.17795, 2026.

[3] S. E. Maleki, M. Pourreza, and D. Rafiei, “Confidence Estimation for Text-to-SQL in Large Language Models,” Proc. AAAI Conf. Artif. Intell., vol. 40, no. 38, pp. 32474–32482, 2026, https://doi.org/10.1609/aaai.v40i38.40523.

[4] Z. Hussain and K. Nielbo, “The Coverage Illusion: From Pre-retrieval Routing Failure to Post-retrieval Cascades in a Production RAG System,” arXiv:2605.27220, 2026.

[5] P. Liskowski, F. Zhao, B. Han, A. Datta, and D. Tsirogiannis, “Compositional Online Learning for Semantic Data Processing Systems,” arXiv:2608.27244, 2026.

[6] K. Chen, Y. Chen, N. Koudas, and X. Yu, “Reliable Text-to-SQL with Adaptive Abstention,” Proc. ACM Manag. Data, vol. 3, no. 1, Art. 69, pp. 1–30, 2025, https://doi.org/10.1145/3709719.

[7] A. S. Pillai, “GROUND: Reducing Hallucinations in LLM-Based Enterprise Analytics Through Governed Semantic Definitions,” arXiv:2608.26157, 2026.

[8] G. Sullutrone, L. Sala, S. Aftar, G. Koutrika, and S. Bergamaschi, “ABISS: Evaluating Text-to-SQL Systems Through Agent Interaction,” arXiv:2607.23340, 2026.

[9] C. Zhao, Z. Peng, Y. Tian, Y. Liu, Y. Su, H. Zhu, L. Zhang, and H. Zeng, “Agentic-SQL Revisited: Autonomy-Based Taxonomy and Empirical Benchmark Analysis for LLM Text-to-SQL,” in Advanced Intelligent Computing Technology and Applications – 22nd International Conference on Intelligent Computing (ICIC 2026), Part XIV, Lecture Notes in Computer Science, vol. 16655, pp. 601–612, Springer, 2026, https://doi.org/10.1007/978-981-92-3438-7_51.

[10] X. Huang, J. Song, P. Li, F. Jiang, J. Zhang, T. Zhang, J. Chen, C. Liu, T. Yang, M. Liu, W. Li, H. Chen, and C. Li, “ACTS-SQL: Agentic and Critic-Oriented Tree-Structured SQL Correctness with Large Language Models,” arXiv:2608.15145, 2026.

[11] H. Zheng, Y. Gou, and W. Zhang, “ZAS-SQL: Distilling Rules from Failures for Zero-Shot Text-to-SQL,” arXiv:2606.08245, 2026.

[12] Y. Liu, J. Lin, Z. Hong, Z. Yuan, S. Chen, H. Chen, Q. Zhang, X. Huang, and F. Huang, “Evaluating LLMs on Conversational Text-to-SQL under Chain Ambiguity and Intent Drift,” arXiv:2608.29543, 2026.

[13] G. Singh, P. Kavehzadeh, J. Xia, X.-Y. Fu, J. B. Tremblay, M. T. R. Laskar, V. Lum, and S. Bhushan TN, “Beyond Text-to-SQL: An Agentic LLM System for Governed Enterprise Analytics APIs,” arXiv:2605.21027, 2026.

[14] Y. Fei, Y. Jiang, Y. Yang, and X. Xiao, “Benchmarking Text-to-SQL under Role-Based Access Control,” arXiv:2607.22115, 2026.

[15] K. Gwimm and C. Eisenach, “Beyond the Harness: End-to-End Optimization of Context Artifacts for Enterprise Text-to-SQL,” arXiv:2608.22830, 2026.

[16] D. Y. Su, S. Y. Su, Q. Sun, Y. Ding, and W. Liu, “Disentangling Structure and Semantics: How Schema Representation Affects LLM-Based SQL Generation,” arXiv:2608.20356, 2026.

[17] T. Lin, Y. Luo, and N. Tang, “Structure then Query: Enabling Precise Analytical Queries over Unstructured Documents,” arXiv:2608.13384, 2026.

[18] “DBLifeBench: Database Lifecycle Benchmark,” arXiv:2608.03794, 2026.

[19] W. Wu, X. Lin, R. Fu, Z. Yu, X. Chen, W. Yu, and Z. Chen, “SQuaD-SQL: Efficient Text-to-SQL with Small Language Models via LLM-Guided Knowledge Distillation,” arXiv:2607.08161, 2026.

[20] Z. Chen, J. Song, and P. Li, “TAHOE: Text-to-SQL with Automated Hint Optimization from Experience,” arXiv:2606.12387, 2026.

[21] R. K. Tummalapenta and S. Addanki, “Memory Architectures for Multi-Turn Text-to-SQL: A Benchmark and Empirical Study,” arXiv:2605.26394, 2026.

[22] R. Ma, S. Shankar, R. Chen, Y. Lin, S. Zeighami, R. Ghosh, A. Gupta, A. Gupta, T. Gopal, and A. Parameswaran, “Can AI Agents Answer Your Data Questions? A Benchmark for Data Agents,” arXiv:2603.20576, 2026.

[23] “BUDDY: Budget-driven dynamic computation depth,” arXiv:2606.09514, 2026.

[24] T. Li, W. Feng, W. Li, A. Wuerkaixi, G. Liu, and Y. Zhang, “Knowing When Not to Reuse: Conditional Experience Transfer in Autonomous LLM Post-Training,” arXiv:2608.26730, 2026.

[25] U. Nisa, M. Shirazi, M. A. Saip, and M. S. M. Pozi, “Agentic AI: The age of reasoning—A review,” J. Automation and Intelligence, vol. 5, no. 1, pp. 69–89, 2026, https://doi.org/10.1016/j.jai.2025.08.003.

[26] Y. Song and A. Zhang, “From black box to physically interpretable: Trustworthy computing for AI-driven decision-making and control,” J. Automation and Intelligence, vol. 5, no. 2, pp. 91–111, 2026, https://doi.org/10.1016/j.jai.2025.09.003.

[27] X. Li, J. You, H. Li, J. Peng, X. Chen, Z. Guo, K. Li, and T. Xu, “G²SQL: guided & guarded Text-to-SQL generation with two-stage verification,” Expert Systems with Applications, vol. 311, Art. 131276, 2026, https://doi.org/10.1016/j.eswa.2026.131276.

[28] A. Birhane, R. Steed, V. Ojewale, B. Vecchione, and I. D. Raji, “AI auditing: The Broken Bus on the Road to AI Accountability,” in 2024 IEEE Conference on Secure and Trustworthy Machine Learning (SaTML), pp. 612–643, 2024, https://doi.org/10.1109/SaTML59370.2024.00037.

[29] Gartner, “From Demo to Production: Closing the AI Agent Reliability Gap,” May 8, 2026. https://www.gartner.com/en/documents/7832217. Accessed September 14, 2026.

[30] Gartner, “Analyst Take: Designate a Defensible AI Architect Now,” May 20, 2026. https://www.gartner.com/en/documents/7887777. Accessed September 14, 2026.

[31] Gartner, “Market Guide for AI Evaluation and Observability Platforms,” February 2, 2026. https://www.gartner.com/en/documents/7387730. Accessed September 14, 2026.

[32] Gartner, “Engineering Trust: The New Hard Skill Essential for Leading AI,” July 7, 2026. https://www.gartner.com/en/documents/8102697. Accessed September 14, 2026.

[33] Gartner, “Use This Framework to Evaluate AI Agents,” June 26, 2026. https://www.gartner.com/en/documents/8061133. Accessed September 14, 2026.

[34] Gartner, “Observability Is a Must for Custom AI Agents and Multiagent Systems,” August 17, 2026. *Final publisher URL to be verified immediately before submission.*

## Submission-control note

This Markdown file is the **canonical JAI-content revision**, not a substitute for the journal's required editable Word/LaTeX submission template. Before submission, the author must transfer the content into the current JAI/Elsevier template, supply the verified affiliation, postal address, corresponding-author email, biography and photograph, verify funding and competing-interest declarations, add final figure/table files and captions, run the final bidirectional citation/reference check, and confirm the rendered manuscript is within JAI's 20-page maximum for a Full-length Research Article.
