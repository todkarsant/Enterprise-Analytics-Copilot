# When Evidence Is Not Enough: Replacement Decisions in Analytical AI Agents

**Santosh Sadashiv Todkar**¹,*  
AI Engineer, Acronotics Private Limited  
507, HBR layout, 1st Stage, 4th Block, Outer Ring Road, Bengaluru 560043, India  
Email: santoshmh09@gmail.com  
ORCID: 0000-0002-7154-3331

**Digvijay Bhosale**²  
Department of Mechanical Engineering, Dr. D. Y. Patil Institute of Technology, Pune, India  
Email: digvijay_bhonsale@yahoo.co.in  
ORCID: 0000-0002-0432-6791

**First author and corresponding author:** Santosh Sadashiv Todkar

## Abstract

AI agents increasingly combine evidence retrieval, analytical execution, verification, and additional reasoning to answer data questions. In such systems, however, identifying an answer as potentially unreliable is different from deciding whether the existing answer should be replaced. This study investigates that distinction in cross-schema Text-to-SQL by separating three decisions: risk detection, intervention, and replacement authorization.

We first evaluate frozen execution policies and a post-evidence cascade, then conduct mechanism forensics and test an incumbent-preserving policy that begins with an existing analytical answer, uses decision-time evidence to determine whether intervention is warranted, and replaces the incumbent only when the challenger satisfies predefined SQL validity, execution, and structural verification checks. Correctness is evaluated using the official Spider execution evaluator, with paired harm–rescue analysis used to characterize replacement decisions.

On 1,034 cases, the incumbent achieves approximately 24.6% execution accuracy, whereas the tested incumbent-preserving policy achieves approximately 22.6% and increases mean cost by approximately 25.8%. Among development cases selected for intervention, 33.87% of correct incumbent answers are harmed, while only 0.75% of incorrect incumbent answers are rescued. The held-out-schema partition shows the same directional pattern.

These results identify a practical reliability boundary: **evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement**. The findings motivate treating risk detection, computational intervention, replacement authorization, and auditability as separate controls in analytical AI systems.

**Keywords:** Analytical agent; Text-to-SQL; Selective prediction; Verification; Auditability

## 1. Introduction

AI systems that answer business questions from data are moving beyond one-shot text generation. An analytical agent may first understand a question, inspect the available data structure, formulate an analytical query, execute it, inspect the result, and decide whether more work is needed. This creates a new reliability question: **what should the system be allowed to do when it is uncertain about an answer it has already produced?**

That question is easy to overlook. Detecting that an answer looks suspicious is one task. Deciding to spend additional computation is another. Deciding that a new answer is strong enough to replace an existing answer is a higher-authority decision. Treating all three as the same “confidence” problem can hide an important failure mode: a system may correctly identify a case as worth investigating while still being unable to determine which answer should ultimately be trusted.

The distinction studied here is summarized in Figure 1.

**Figure 1. From suspicion to decision authority**

```text
        CURRENT ANSWER
              │
              ▼
      ┌─────────────────┐
      │  1. RISK        │  Is something suspicious?
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │  2. INTERVENE   │  Is more work worth doing?
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │  3. REPLACE     │  Is the new answer safe enough
      │                  │  to discard the old one?
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │  4. AUDIT       │  Can the decision be reconstructed?
      └─────────────────┘
```

The central proposition is deliberately simple:

> **Evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.**

We examine this proposition in a controlled Text-to-SQL setting. The research question is:

> **Under a cross-schema Text-to-SQL workload, can an evidence-triggered incumbent-preserving policy improve the harm–rescue–cost trade-off relative to a frozen incumbent analytical policy?**

The paper is intentionally conservative about novelty. Agentic Text-to-SQL, adaptive routing, abstention, execution-guided correction, verification, enterprise governance, and AI auditing are established areas of research [1–28]. The contribution claimed here is narrower: an empirical separation of **risk detection, intervention selection, and replacement authorization**, evaluated through paired harm–rescue analysis, together with a defensibility-oriented record for reconstructing the decision path.

The result is a negative but informative one. In the tested setting, the evidence and verification available to the challenger were not sufficiently reliable to replace the incumbent safely. The study therefore treats failure as a boundary condition to be measured rather than as a result to be engineered away.

## 2. Related Work and Literature Positioning

### 2.1 Correctness prediction and verification

Correctness estimation for Text-to-SQL is already an active research problem. Maleki et al. study black-box and white-box confidence estimation and show that execution-based grounding can provide useful supplementary evidence [3]. Richardson studies selective prediction using structural, execution, and self-consistency signals and highlights the difficulty of reliable correctness discrimination across schemas [1]. TraceSQL similarly investigates reference-free answerability estimation using explicit diagnostic evidence [2]. These studies make clear that structural and execution signals should not be presented as a new verification principle.

Reliable Text-to-SQL with Adaptive Abstention treats abstention and human interaction as reliability controls, including statistical treatment of schema-linking uncertainty [6]. Project 1 therefore does not claim to invent safe abstention or uncertainty-aware interaction.

G²SQL is an especially important comparator because it uses a guided and guarded two-stage verification architecture with a Reviewer–Observer mechanism [27]. The verification gate tested here is deliberately much simpler: SQL validity, successful execution, and selected structural checks. Consequently, a negative result for this gate should **not** be interpreted as evidence that stronger verification is ineffective.

### 2.2 Adaptive computation and cascades

Adaptive computation is also well established. The Coverage Illusion studies post-retrieval escalation in a production RAG system [4]. Compositional Online Learning for Semantic Data Processing Systems makes execution-time decisions and includes semantic SQL cascade routing [5]. Agentic-SQL Revisited provides a published taxonomy and empirical analysis of Text-to-SQL autonomy [9]. ACTS-SQL uses correction, backtracking, execution-based verification and clause-level diagnostics [10]. ZAS-SQL uses failure-derived rules and execution-guided stopping [11], while TAHOE learns reusable hints from debugging and execution experience [20].

Accordingly, the present work does not claim novelty for adaptive routing, post-evidence escalation, cost-aware computation, agentic SQL, or execution-guided correction. These mechanisms form part of the prior-art boundary against which the experiment is interpreted.

### 2.3 Enterprise analytical reliability

Enterprise analytical systems introduce concerns that are not visible in a simple SQL accuracy number. GROUND considers governed semantic definitions, joins, grain, filters, security, and cost rules [7]. Beyond Text-to-SQL describes governed enterprise analytics APIs with permission validation and policy-aware orchestration [13]. RBAC-aware Text-to-SQL benchmarking demonstrates that unrestricted benchmark accuracy can conceal authorization failures [14]. DAB evaluates broader data-agent workloads, while EnterpriseMem-Bench and ABISS examine multi-turn memory and interactive ambiguity respectively [8,21,22].

Other recent work shows that the context supplied to a Text-to-SQL system, and the way schema structure and semantics are represented, can materially affect performance [15–19]. These studies reinforce the need to distinguish the controlled benchmark question from claims about enterprise deployment.

### 2.4 Auditability and trustworthy decision-making

Birhane et al. distinguish AI auditing activity from accountability and emphasize the importance of audit design, methodology, and institutional context [28]. Project 1 therefore uses **auditability** in a deliberately limited sense: preserving evidence needed to reconstruct a system decision. It does not claim legal compliance or complete institutional accountability.

Recent Journal of Automation and Intelligence work emphasizes the growing importance of agentic reasoning and trustworthy decision-making, including reliability, robustness, verifiability, safety, and explicit constraints [25,26]. These papers support the broader research framing but do not establish the specific contribution tested here. Similarly, current industry research from Gartner emphasizes reliability, evaluation, observability, defensibility, challenge, transparency, and accountability for AI agents [29–34]. These sources are used as industry-context evidence rather than as evidence of academic novelty.

### 2.5 The narrow gap

The literature contains substantial work on predicting correctness, routing computation, escalating after evidence, verifying SQL, abstaining, governing enterprise analytics, and auditing AI systems. The narrower question examined here is whether **evidence useful for deciding to investigate is also strong enough to authorize replacement of an incumbent analytical answer**.

That distinction makes four outcomes directly observable:

1. **Rescue:** the incumbent is wrong and the challenger is correct.
2. **Harm:** the incumbent is correct and the challenger is wrong.
3. **Preserved-correct:** the incumbent is correct and remains selected.
4. **Preserved-wrong:** the incumbent is wrong but remains selected.

The experiment measures these outcomes directly rather than compressing them into one confidence score.

## 3. Research Design

### 3.1 A falsification-first study

The research was designed as a sequence of increasingly demanding tests. Each stage was allowed to fail.

**Figure 2. Research progression**

```text
Literature audit
      │
      ▼
Reject broad “adaptive routing is novel” claim
      │
      ▼
Freeze P0–P5 baselines
      │
      ▼
Investigate P5 failure mechanism (P5R)
      │
      ▼
Test incumbent-preserving P6-IP
      │
      ▼
Measure harm versus rescue
      │
      ▼
┌───────────────────────────────┐
│ Stop further algorithmic      │
│ escalation if the trade-off   │
│ remains unfavorable.          │
└───────────────────────────────┘
```

P0–P5 were frozen before the final challenger. P5R was mechanism forensics and did not modify the frozen baselines. P6-IP was explicitly defined as the final controlled challenger. The predefined stop rule was to stop algorithmic escalation if incumbent harm remained materially larger than rescue without a favorable cost trade-off.

### 3.2 What is Spider?

Spider is a public benchmark for **Text-to-SQL**: the system receives a natural-language question together with a database schema and must produce SQL that answers the question. Its value for this study is that the benchmark spans multiple database schemas, allowing the evaluation to test whether a policy behaves consistently when the underlying data structure changes.

Spider is used here as a **controlled research environment**, not as a proxy for a complete enterprise deployment. It does not by itself provide real organizational permissions, governed business definitions, production workload variability, or institutional accountability. The benchmark therefore lets us test the decision mechanism under reproducible conditions while keeping the enterprise interpretation appropriately bounded.

### 3.3 Dataset and partitions

The research artifact contains 1,034 cases. A schema-level split with seed 1729 assigns four schemas—`car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`—to a 254-case held-out-schema partition. The remaining 16 schemas form a 780-case development partition.

The 254 cases are therefore a partition of the 1,034-case artifact rather than an independent second dataset. The held-out schemas are used for locked observational corroboration, not as a separate source of tuning data.

### 3.4 Experimental contract

| Item | Locked value |
|---|---|
| Total cases | 1,034 |
| Development partition | 780 |
| Held-out-schema partition | 254 |
| Holdout fraction | 20% |
| Split seed | 1729 |
| Official evaluator | Spider commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c` |
| Execution model | Process-isolated |
| Parent timeout | 150 s |
| Runtime chunks | 12 |
| Iterative model | Ollama `llama3.2:1b` |
| Paid/Azure inference | Not used |

Official Spider execution accuracy is the primary correctness measure. Custom row-set equality is retained only as a diagnostic. Runtime failures and timeouts remain in the denominator.

### 3.5 Policy ladder

The policies represent increasingly adaptive ways of deciding how much analytical work to perform.

**Figure 3. From fixed execution to evidence-dependent replacement**

```text
                 HOW MUCH WORK SHOULD WE DO?
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
   FIXED WORK            SELECTIVE WORK        REPLACEMENT WORK
       │                      │                      │
       ▼                      ▼                      ▼
 P0 Always-LLM         P3/P4 Query-time       P5 Post-evidence
 P1 Deterministic     routing/heuristics      cascade
 P2 Static Hybrid                              │
                                               ▼
                                         P5R mechanism
                                           forensics
                                               │
                                               ▼
                                      P6-IP incumbent
                                      preservation gate
```

P0 is the frozen incumbent: an always-LLM analytical policy. P1 is deterministic-only. P2 is a static hybrid. P3 is a query-complexity router. P4 is a query-only heuristic confidence router. P5 is a post-evidence cascade. P2 and P3 produced identical behavior under the implemented decision rule and are therefore not interpreted as independent successful mechanisms. P4 is a deterministic heuristic, not a calibrated confidence estimator.

### 3.6 P6-IP: making replacement a higher-authority action

P6-IP starts with the P0 answer already in hand. It does not assume that a suspicious signal automatically earns the right to replace that answer.

**Figure 4. Incumbent-preserving decision flow**

```text
                 ┌─────────────────┐
                 │  P0 INCUMBENT   │
                 │  existing answer│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Evidence / risk │
                 │ assessment      │
                 └────────┬────────┘
                          │
                    ┌─────┴─────┐
                    │           │
                  KEEP      INTERVENE
                    │           │
                    │           ▼
                    │    ┌──────────────┐
                    │    │  Challenger   │
                    │    └──────┬───────┘
                    │           │
                    │           ▼
                    │    ┌──────────────┐
                    │    │ Verification │
                    │    └──────┬───────┘
                    │           │
                    │      ┌────┴────┐
                    │      │         │
                    │    REJECT    ACCEPT
                    │      │         │
                    ▼      ▼         ▼
                 PRESERVE PRESERVE  REPLACE
                 INCUMBENT INCUMBENT CHALLENGER
```

The tested verification gate requires three conditions: valid challenger SQL, successful execution, and structural consistency with detected question requirements. It does **not** establish semantic equivalence between incumbent and challenger results, and it does not use a separate high-strength reasoning verifier.

### 3.7 Decision-time evidence versus post-hoc evidence

A central integrity control is the separation between what the policy could know when making its decision and what researchers learn afterward.

```text
DECISION TIME                         POST-HOC ANALYSIS
─────────────                         ─────────────────
Question                              Gold answer
Evidence observed                     Official correctness
Evidence provenance          ≠       Statistical tests
Risk reason                           Confidence intervals
KEEP / INTERVENE                      Failure taxonomy
Challenger + verification             Comparative analysis
```

The official evaluator therefore cannot act as an oracle inside the policy. It is used after execution to determine whether the final answer was correct.

### 3.8 Outcomes and statistical analysis

The primary measures are official execution accuracy, paired correctness, incumbent harm, rescue, intervention rate, mean cost, and latency. Secondary measures include replacement and rejection rates, model calls, token use, latency tails, runtime failures, decision-trace completeness, and evidence-provenance completeness.

Paired correctness differences use exact two-sided McNemar tests. Continuous paired differences use bootstrap confidence intervals. Wilson intervals are used for harm and rescue proportions. The 90%, 95%, 97%, and 99% reliability levels are retained as diagnostic targets, not production guarantees.

## 4. Results

### 4.1 Frozen baseline results

The frozen policies provide an important reference point before considering replacement. P0, the incumbent, achieved 254 correct cases out of 1,034 (approximately 24.6%). P1 achieved 0; P2 and P3 each achieved 256 (approximately 24.8%); P4 achieved 20 (approximately 1.9%); and P5 achieved 123 (approximately 11.9%).

P5 reduced mean cost by approximately 9.35% relative to P0, but this saving came with a large accuracy loss. P0 was correct while P5 was wrong on 158 cases; P5 rescued 27 cases where P0 was wrong. The exact paired McNemar p-value was approximately 1 × 10^-23.

The baseline therefore established a useful warning: reducing computation is not equivalent to improving reliability.

### 4.2 P5R mechanism forensics

P5R was introduced to understand why the post-evidence cascade underperformed; it was not introduced to rewrite the frozen baseline. On the 1,034-case artifact, P5R achieved 179/1,034 (approximately 17.3%) official accuracy. Its paired difference versus P0 was approximately −7.25 percentage points, and its mean cost was higher than P5.

Diagnostic evidence features contained predictive signal, but they did not provide sufficient evidence for safe incumbent replacement. This analysis was post-hoc and was not used to tune the held-out partition.

### 4.3 P6-IP primary result

P6-IP achieved 234/1,034 (approximately 22.6%) official execution accuracy on development, compared with 254/1,034 (approximately 24.6%) for P0. The paired difference was approximately −1.93 percentage points, with exact McNemar p = 0.001193. Mean cost increased from approximately 0.269 to 0.338, an increase of approximately 25.8%.

The paired outcomes were:

| Outcome | Cases |
|---|---:|
| Both correct | 226 |
| P0 correct, P6-IP wrong | 28 |
| P6-IP correct, P0 wrong | 8 |
| Both wrong | 772 |

The challenger therefore changed 36 paired outcomes, with substantially more harmful changes than rescues.

### 4.4 Harm–rescue analysis

The most informative result comes from the cases in which P6-IP actually intervened.

| Partition | Intervention-eligible | P0-correct eligible | P0-wrong eligible | Harm | Rescue |
|---|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 |
| Held-out schemas | 91 | 16 | 75 | 5 | 1 |

For development, 21 of 62 correct incumbent answers selected for intervention were harmed, approximately **33.87%**. Only 2 of 268 incorrect incumbent answers selected for intervention were rescued, approximately **0.75%**. Correctness-changing interventions were 23/330, approximately 6.97%, producing a net intervention contribution of −19 cases.

The held-out-schema partition shows the same direction: 5 of 16 correct incumbent answers selected for intervention were harmed, 31.25%, while only 1 of 75 incorrect incumbents was rescued, approximately 1.33%. This is observational corroboration because of the historical ordering of the holdout execution; the development result independently triggered the stop rule.

**Figure 5. The replacement asymmetry**

```text
                 INTERVENTION
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     INCUMBENT CORRECT       INCUMBENT WRONG
          │                       │
          ▼                       ▼
       HARM                    RESCUE
     21 / 62                 2 / 268
      33.87%                   0.75%
          │                       │
          └───────────┬───────────┘
                      ▼
          Replacement evidence
          was not sufficiently
          selective for safety
```

This asymmetry is the central empirical finding of the study.

### 4.5 Reliability, cost and latency

P6-IP did not meet the predefined 90%, 95%, 97%, or 99% diagnostic reliability targets. Mean cost increased by approximately 25.8% on development and approximately 29.2% on the held-out-schema partition.

Development median latency was approximately 2.10 s for P6-IP versus 2.00 s for P0; development P95 latency was approximately 13.6 s versus 5.6 s. Holdout P95 latency was approximately 24.8 s for P6-IP versus 7.4 s for P0.

These latency tails matter because an intervention policy can look acceptable at the median while imposing substantial delay on difficult cases.

## 5. Discussion

### 5.1 The main finding in plain language

The strongest supported statement is:

> **Under the tested Spider cross-schema setting, decision-time evidence combined with executable and structural verification did not provide a sufficiently favorable harm–rescue trade-off for incumbent replacement.**

In plain language:

> **The system could find reasons to look again, but those reasons were not reliable enough to justify throwing away the current answer.**

This is a conditional empirical result. It does not establish that stronger verifiers, larger models, different enterprise datasets, or other evidence policies would fail.

### 5.2 Why the negative result matters

The failure is more informative than simply saying that P6-IP was less accurate. The paired intervention analysis identifies a mechanism-level problem. The policy was allowed to intervene in 330 development cases. Among cases where the incumbent was correct, the intervention harmed 21; among cases where the incumbent was wrong, it rescued only 2.

This separates three concepts often compressed into “confidence”:

1. **Risk detection:** evidence that the incumbent may be wrong.
2. **Intervention value:** evidence that additional computation is worth its cost.
3. **Replacement authorization:** evidence strong enough to discard the incumbent.

A signal can be useful for the first or second decision without being safe for the third.

### 5.3 What this does not show

The verification gate tested here was intentionally limited. It checked SQL validity, execution, and structural cues, but did not compare semantic result equivalence or use a strong independent reasoning verifier. Recent work such as G²SQL demonstrates richer two-stage verification [27]. The present result therefore bounds the tested verification mechanism; it does not show that stronger verification is ineffective.

Likewise, Spider is a controlled cross-schema Text-to-SQL benchmark, not an enterprise production environment. The experiment does not establish production readiness, authorization correctness, regulatory compliance, or universal reliability.

### 5.4 Implications for analytical AI systems

For business leaders, the practical distinction is straightforward. A system may be allowed to **investigate** a suspicious answer at relatively low authority, but **replacing** an existing answer should require stronger evidence.

This suggests a layered control model:

```text
          CAN WE TRUST THIS ANSWER?
                     │
                     ▼
              RISK DETECTION
                     │
                     ▼
            SHOULD WE LOOK AGAIN?
                     │
                     ▼
               INTERVENTION
                     │
                     ▼
          IS THE NEW ANSWER SAFE?
                     │
                     ▼
        REPLACEMENT AUTHORIZATION
                     │
                     ▼
             AUDITABLE RECORD
```

The Defensibility Layer developed in this project supports the final step by preserving evidence provenance, policy rationale, verification results, authorization hooks, outcomes, cost, and reproducibility information. It is an auditability mechanism, not a claim of legal compliance or complete governance.

### 5.5 Research boundary and future work

The appropriate next research direction is not another routing heuristic built on the same evidence. Stronger semantic verification, calibrated replacement authorization, selective prediction, and evaluation under governed enterprise workloads are more direct ways to test whether the observed harm–rescue asymmetry can be reduced.

## 6. Threats to Validity

**Incumbent weakness.** P0 is only approximately 24.6% accurate. This limits absolute performance claims. The paired harm/rescue analysis remains informative because every policy sees the same cases.

**Small model.** The final controlled experiments use `llama3.2:1b`, limiting generalization to stronger models.

**Verification strength.** The gate is weaker than recent multi-stage verifiers. The result therefore bounds the tested mechanism rather than verification as a field.

**Benchmark transfer.** Spider is not an enterprise deployment benchmark.

**Holdout ordering.** The historical held-out-schema execution preceded complete development aggregation. It is therefore reported as observational corroboration rather than fully prospective confirmation.

**Post-hoc diagnostics.** Diagnostic models were used for mechanism understanding only. They did not become part of the P6-IP decision rule or tune the held-out partition.

**Multiple comparisons.** The primary P6-IP comparison is paired and prespecified. Additional analyses are treated as supporting diagnostics rather than independent discovery claims.

## 7. Conclusion

This study examined whether evidence available during analytical execution is sufficient not only to justify further investigation, but also to authorize replacement of an existing answer. The experiments were deliberately structured to distinguish these decisions rather than treating them as a single notion of confidence or routing.

The evidence does not support the tested replacement policy. On the 1,034-case development artifact, the incumbent P0 achieved approximately 24.6% execution accuracy, while P6-IP achieved approximately 22.6% and increased mean cost by approximately 25.8%. More importantly, the paired intervention analysis exposed the mechanism-level failure: among intervention-eligible development cases for which the incumbent was correct, approximately 33.9% were harmed, whereas only approximately 0.75% of intervention-eligible cases with an incorrect incumbent were rescued. The held-out-schema partition exhibited the same directional pattern.

The result is therefore stronger than a simple statement that one policy performed worse than another. It demonstrates that **risk detection, intervention selection, and replacement authorization are not interchangeable decisions**. Evidence may be sufficiently informative to justify spending additional computation while remaining insufficiently reliable to justify discarding an answer that is already correct. In the tested setting, executable and structural verification did not provide a sufficiently favorable safeguard against this replacement risk.

This negative result is bounded. The experiments use the Spider cross-schema Text-to-SQL workload and `llama3.2:1b`; the verification gate does not perform semantic equivalence checking or employ a stronger independent reasoning verifier. Consequently, the findings do not establish that stronger models, stronger verifiers, different datasets, or alternative evidence policies would exhibit the same boundary.

The practical implication is that analytical agents should treat replacement as a higher-authority action than investigation. A defensible architecture should preserve the incumbent unless a challenger satisfies an independently justified replacement criterion, while recording the evidence, policy decision, verification outcome, provenance, cost, and resulting action for later audit. The Defensibility Layer developed in this work provides an architectural mechanism for preserving that evidence, but does not by itself establish regulatory compliance or production governance.

The principal research boundary established by this study is therefore concise: **an agent can have enough evidence to know that something may be wrong without having enough evidence to safely change the answer**. Future work should focus on stronger semantic verification, calibrated replacement authorization, selective prediction, and evaluation under governed enterprise workloads rather than extending the present routing mechanism without resolving the observed harm–rescue asymmetry.

## 8. Reproducibility and Data Availability

The public Spider benchmark and research code required for the reported analyses are maintained in the repository. The official evaluator is pinned to commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`. P6-IP was executed in GitHub Actions with local Ollama inference; paid/Azure inference was not used.

The development artifact contains 1,034 cases and the locked held-out-schema partition contains 254 cases. Runtime traces, decision records, provenance manifests, statistical analysis scripts, tests, and workflow definitions are retained in the repository or associated research artifacts where applicable.

The manuscript's research chain is anchored to repository history rather than to a mutable benchmark result. Reproduction should verify the cited commits, run identifiers, evaluator version, and artifact manifests against the repository.

**Data availability:** The Spider dataset is publicly available from its original distribution. Project-specific derived traces and analysis artifacts are maintained with the repository subject to repository/artifact availability constraints.

## 9. Code Availability

Source code, evaluation scripts, policy implementations, tests, workflow definitions, and analysis utilities are maintained in the project repository: `todkarsant/Enterprise-Analytics-Copilot`.

The canonical manuscript branch is `research/paper-lit-integration`. The manuscript and reviewer-facing reproducibility map are anchored in the repository history. The reproducibility map at `docs/PROJECT1_REPRODUCIBILITY_MAP.md` provides the detailed routing from the manuscript to immutable commits, experimental runs, evaluator version, corrected artifacts, analysis scripts, and research-state controls.

For the controlled P6-IP experiment, the principal execution anchor is GitHub Actions run `34252265013`, with controlled-run head `ffb4cc5ecf8b762af03ddb42ecf401c1957e640`. The frozen official evaluator is pinned to `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`. The manuscript should be interpreted together with the reproducibility map rather than as the sole provenance record.

## 10. Funding

**Funding:** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## 11. Declaration of Competing Interest

**Competing interests:** The authors declare that they have no competing financial or personal interests that could have influenced this work.

## 12. Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

During preparation of this manuscript, the authors used OpenAI ChatGPT to assist with language editing, structural revision and preparation of publication-oriented text. The authors reviewed and edited the resulting material and take full responsibility for the accuracy, integrity and final content of the manuscript.

## 13. Author Contributions

**Santosh Sadashiv Todkar:** Conceptualization; Methodology; Software; Investigation; Formal analysis; Data curation; Visualization; Writing – original draft; Project administration; overall experimental execution and research coordination.

**Digvijay Bhosale:** Validation; Writing – review & editing; review of experimental findings; contribution of insights concerning interpretation and validation of the experimental findings.

Both authors reviewed and approved the manuscript for submission and agree to be accountable for the work.

## 14. Acknowledgements

The authors thank the open-source Spider benchmark and evaluation ecosystem and the maintainers of the tools used to reproduce the controlled experiments. No external scientific claim is attributed to these resources beyond their documented role in the experiment.

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

[34] Gartner, “Observability Is a Must for Custom AI Agents and Multiagent Systems,” August 17, 2026. https://www.gartner.com/en/documents/8271421. Accessed September 14, 2026.

## Plagiarism-screening status

This copy is the canonical scientific content at the time of preparation for originality screening. It intentionally excludes final JAI production formatting, biographies, photographs, pagination, and other deferred submission-layout items. Those should be applied only after the originality result and final audit.
