# When Evidence Is Not Enough: Replacement Decisions in Analytical AI Agents

**Santosh Sadashiv Todkar**¹,*  
AI Engineer, Acronotics Private Limited  
507, HBR layout, 1st Stage, 4th Block, Outer Ring Road, Bengaluru 560043, India  
Email: santoshmh09@gmail.com  
ORCID: https://orcid.org/0000-0002-7154-3331

**Digvijay Bhosale**²  
Department of Mechanical Engineering, Dr. D. Y. Patil Institute of Technology, Pune, India  
Email: digvijay_bhonsale@yahoo.co.in  
ORCID: https://orcid.org/0000-0002-0432-6791

**First author and corresponding author:** Santosh Sadashiv Todkar

> **Working manuscript format:** This Markdown manuscript is maintained in a single-column, plagiarism-check-friendly form. Final JAI production formatting, figures, biographies, and pagination will be completed after originality screening and final audit.

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

G²SQL is an especially important comparator because it uses a guided and guarded two-stage verification architecture with a Reviewer–Observer mechanism [27]. The verification gate tested here is deliberately much simpler: SQL validity, successful execution, and selected structural checks. Consequently, a negative result for this gate should **not** be interpreted as evidence that stronger verification is ineffective. GradeSQL further illustrates a stronger test-time verification direction by using outcome reward models to rank candidate SQL queries on semantic correctness and schema alignment, reporting gains over execution-based heuristics on Spider and BIRD [35].

### 2.2 Adaptive computation and cascades

Adaptive computation is also well established. The Coverage Illusion studies post-retrieval escalation in a production RAG system [4]. Compositional Online Learning for Semantic Data Processing Systems makes execution-time decisions and includes semantic SQL cascade routing [5]. Agentic-SQL Revisited provides a published taxonomy and empirical analysis of Text-to-SQL autonomy [9]. ACTS-SQL uses correction, backtracking, execution-based verification and clause-level diagnostics [10]. ZAS-SQL uses failure-derived rules and execution-guided stopping [11], while TAHOE learns reusable hints from debugging and execution experience [20].

Accordingly, the present work does not claim novelty for adaptive routing, post-evidence escalation, cost-aware computation, agentic SQL, or execution-guided correction. These mechanisms form part of the prior-art boundary against which the experiment is interpreted. Recent Journal of Intelligent Information Systems work also shows that structured multi-agent deliberation can improve performance on some high-complexity tasks while a single agent can remain stronger when retrieval alone is sufficient, reinforcing that additional reasoning should be evaluated conditionally rather than assumed to be beneficial [36].

### 2.3 Enterprise analytical reliability

Enterprise analytical systems introduce concerns that are not visible in a simple SQL accuracy number. GROUND considers governed semantic definitions, joins, grain, filters, security, and cost rules [7]. Beyond Text-to-SQL describes governed enterprise analytics APIs with permission validation and policy-aware orchestration [13]. RBAC-aware Text-to-SQL benchmarking demonstrates that unrestricted benchmark accuracy can conceal authorization failures [14]. DAB evaluates broader data-agent workloads, while EnterpriseMem-Bench and ABISS examine multi-turn memory and interactive ambiguity respectively [8,21,22].

Other recent work shows that the context supplied to a Text-to-SQL system, and the way schema structure and semantics are represented, can materially affect performance [15–19]. Applied Intelligence research likewise reports that knowledge-graph-extended retrieval can improve robustness and explainability in LLM-based question answering, while weighted verification and ranking can filter generated knowledge prompts before they are supplied to an LLM [37,38]. These studies reinforce the need to distinguish the controlled benchmark question from claims about enterprise deployment.

### 2.4 Auditability and trustworthy decision-making

Birhane et al. distinguish AI auditing activity from accountability and emphasize the importance of audit design, methodology, and institutional context [28]. Project 1 therefore uses **auditability** in a deliberately limited sense: preserving evidence needed to reconstruct a system decision. It does not claim legal compliance or complete institutional accountability.

Recent Journal of Automation and Intelligence work emphasizes the growing importance of agentic reasoning and trustworthy decision-making, including reliability, robustness, verifiability, safety, and explicit constraints [25,26]. These papers support the broader research framing but do not establish the specific contribution tested here. IEEE Transactions on Artificial Intelligence research also highlights that benchmark integrity, evaluator diversity, implementation consistency, and measurement methodology can materially affect conclusions about LLM capability [39]. In a different verification-oriented setting, TrumorGPT uses graph-based retrieval and semantic reasoning for fact-checking, illustrating how external evidence can be incorporated to address hallucination and improve factual verification [40]. Similarly, current industry research from Gartner emphasizes reliability, evaluation, observability, defensibility, challenge, transparency, and accountability for AI agents [29–34]. These sources are used as industry-context evidence rather than as evidence of academic novelty.

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

### 4.1 What happened with the frozen baselines?

| Policy | Correct / 1,034 | Accuracy |
|---|---:|---:|
| P0 | 254 | 24.565% |
| P1 | 0 | 0.000% |
| P2 | 256 | 24.758% |
| P3 | 256 | 24.758% |
| P4 | 20 | 1.934% |
| P5 | 123 | 11.896% |

P5 reduced mean cost by approximately 9.35% relative to P0, but its accuracy was much lower. P0 was correct while P5 was wrong on 158 cases, whereas P5 rescued 27 cases on which P0 was wrong. The exact paired McNemar p-value was approximately 1 × 10^-23.

The practical message is important: **doing less model work did save cost, but the saving came with a substantial loss of correctness**. P5 was therefore not a suitable reliability-improving replacement for the incumbent.

### 4.2 What did mechanism forensics reveal?

P5R was introduced only to understand why the post-evidence cascade was failing. It achieved 179/1,034 = 17.311% official accuracy on the development artifact, compared with 24.565% for P0. The paired difference versus P0 was −7.253 percentage points. P5R also increased cost relative to P5.

The diagnostic evidence features contained predictive signal, but they were not sufficiently aligned with incumbent correctness to authorize replacement safely. Because these diagnostics were used for mechanism understanding rather than policy tuning, they do not convert into a new deployable reliability claim.

### 4.3 The final P6-IP test

On the 1,034-case development artifact, P6-IP achieved 234/1,034 = 22.631% official execution accuracy versus 254/1,034 = 24.565% for P0. The paired difference was −1.934 percentage points, with exact McNemar p = 0.001193. Mean cost increased from approximately 0.269 to 0.338, an increase of approximately 25.8%.

The paired outcomes were:

| Outcome | Cases |
|---|---:|
| Both correct | 226 |
| P0 correct, P6-IP wrong | 28 |
| P6-IP correct, P0 wrong | 8 |
| Both wrong | 772 |

Thus, even after adding an incumbent-preservation mechanism, more incumbent-correct cases were lost than incumbent-wrong cases were rescued.

### 4.4 The key result: harm versus rescue

| Partition | Eligible interventions | P0-correct eligible | P0-wrong eligible | Harm | Rescue |
|---|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 |
| Held-out schemas | 91 | 16 | 75 | 5 | 1 |

For development, harm among P0-correct intervention-eligible cases was 21/62 = **33.87%**, while rescue among P0-wrong intervention-eligible cases was 2/268 = **0.75%**. Correctness-changing interventions were 23/330 = 6.97%, producing a net intervention contribution of −19 cases.

The held-out-schema partition showed the same direction: harm was 5/16 = **31.25%**, while rescue was 1/75 = **1.33%**. Because the historical holdout execution occurred before complete development aggregation and freeze, this is reported as locked observational corroboration rather than fully prospective confirmation. No holdout result was used for tuning, and the development result alone triggered the stop rule.

**Figure 5. The asymmetry that determines the decision**

```text
          WHEN THE SYSTEM INTERVENES

       INCUMBENT CORRECT          INCUMBENT WRONG
              │                         │
              ▼                         ▼
       ┌──────────────┐          ┌──────────────┐
       │  Challenger  │          │  Challenger  │
       │    wrong     │          │    correct   │
       └──────┬───────┘          └──────┬───────┘
              │                         │
              ▼                         ▼
           HARM: 21                 RESCUE: 2
              │                         │
              └──────────┬──────────────┘
                         ▼
              Harm greatly exceeds rescue
```

The held-out partition provides the same qualitative signal, although its execution ordering means it should not be described as a fully prospective confirmatory experiment.

### 4.5 Reliability targets

P6-IP did not meet the predefined 90%, 95%, 97%, or 99% diagnostic reliability targets on either partition. These levels are not interpreted as evidence that such reliability is impossible in other systems; the frozen incumbent itself has low absolute accuracy in this benchmark setting.

### 4.6 Cost and latency

P6-IP increased mean cost by approximately 25.8% on development and approximately 29.2% on the held-out-schema partition. Development median latency was approximately 2.10 s for P6-IP versus 2.00 s for P0; development P95 latency was approximately 13.6 s versus 5.6 s. Holdout P95 latency was approximately 24.8 s for P6-IP versus 7.4 s for P0.

This matters operationally because a policy can look acceptable at the median while imposing substantial delay on the cases that trigger additional reasoning.

## 5. Discussion

### 5.1 What the experiment establishes

The strongest supported statement is:

> **Under the tested Spider cross-schema setting, decision-time evidence combined with executable and structural verification did not provide a sufficiently favorable harm–rescue trade-off for incumbent replacement.**

In business terms:

> **The system could find reasons to look again, but those reasons were not reliable enough to justify throwing away the current answer.**

This is a conditional empirical result. It does not establish that stronger verifiers, larger models, different enterprise datasets, or alternative evidence policies would fail.

### 5.2 Why the negative result is useful

The result is not simply that “P6-IP was less accurate.” The intervention analysis identifies the mechanism-level problem. The policy was allowed to intervene in 330 development cases. When the incumbent was already correct, intervention harmed 21 cases. When the incumbent was wrong, intervention rescued only 2 cases.

This exposes a distinction that is often hidden inside a single confidence score:

```text
Can I see a reason to doubt the answer?
                │
                ▼
       RISK DETECTION
                │
                ▼
Is it worth spending more computation?
                │
                ▼
      INTERVENTION VALUE
                │
                ▼
Is the new answer strong enough to discard the old one?
                │
                ▼
    REPLACEMENT AUTHORIZATION
```

A signal can be useful for the first decision without being safe for the third. That is the central empirical boundary observed in this study.

### 5.3 The verification boundary

The verification gate used in P6-IP checked validity, execution, and structural cues. It did not compare semantic result equivalence and did not use a strong independent reasoning verifier. Recent published work such as G²SQL demonstrates richer two-stage verification [27], while correctness-prediction research indicates that stronger reasoning-based verification can outperform simple structural and execution signals [1,3].

Therefore, the correct interpretation is not “verification does not work.” It is narrower: **the tested verification class was not sufficient to provide a favorable harm–rescue trade-off in this setting**.

### 5.4 The benchmark boundary

Spider is useful because it gives a controlled cross-schema environment in which the same decision mechanism can be tested across different database structures. It is not an enterprise production benchmark. It does not reproduce organizational permissions, governed metric definitions, business-specific semantic rules, real production workloads, or institutional accountability.

The enterprise relevance of the study is consequently methodological and architectural. The paper studies a decision-authority problem that can arise in enterprise analytical systems, while using Spider as a reproducible public test environment.

### 5.5 The model boundary

The final controlled experiments use local Ollama inference with `llama3.2:1b`. This makes the experiment reproducible and avoids paid inference during iteration, but it also limits generalization. The result should not be presented as a claim about frontier models. A stronger model could change both incumbent quality and the value of verification and therefore requires a separate experiment.

### 5.6 Defensibility: preserving the evidence behind the decision

Correctness and auditability answer different questions.

A benchmark evaluator asks:

> **Was the final answer correct?**

A defensible analytical system also needs to support questions such as:

> **What did the system know when it acted?**  
> **What evidence triggered the action?**  
> **Which policy rule was applied?**  
> **Which verification and authorization controls were used?**  
> **What happened, and can the decision be reconstructed later?**

The Defensibility Layer therefore records evidence provenance, policy rationale, verification, authorization hooks, outcome, cost, and reproducibility separately from post-hoc correctness labels.

**Figure 6. What a defensible analytical decision leaves behind**

```text
QUESTION
   │
   ▼
ANALYTICAL ACTION ──────► EVIDENCE
   │                         │
   │                         ▼
   │                    POLICY / RISK
   │                         │
   │                         ▼
   └────────────────► VERIFICATION
                             │
                             ▼
                         OUTCOME
                             │
                             ▼
                    ┌──────────────────┐
                    │ DECISION RECORD  │
                    │ • evidence       │
                    │ • provenance     │
                    │ • policy reason  │
                    │ • controls       │
                    │ • outcome        │
                    │ • cost / latency │
                    │ • reproducibility│
                    └──────────────────┘
```

This layer supports defensible engineering and later reconstruction; it does not prove legal compliance, institutional accountability, or production governance.

## 6. Conclusion

This study asked whether evidence available during analytical execution is sufficient not only to justify further investigation, but also to authorize replacement of an existing answer. The experiments were deliberately structured to distinguish these decisions rather than treating them as one notion of confidence or routing.

The evidence does not support the tested replacement policy. On the 1,034-case development artifact, the incumbent P0 achieved approximately 24.6% execution accuracy, while P6-IP achieved approximately 22.6% and increased mean cost by approximately 25.8%. More importantly, the paired intervention analysis exposed the mechanism-level failure: among intervention-eligible development cases for which the incumbent was correct, approximately 33.9% were harmed, whereas only approximately 0.75% of intervention-eligible cases with an incorrect incumbent were rescued. The held-out-schema partition exhibited the same directional pattern.

The result is therefore stronger than a simple statement that one policy performed worse than another. It demonstrates that **risk detection, intervention selection, and replacement authorization are not interchangeable decisions**. Evidence may be sufficiently informative to justify spending additional computation while remaining insufficiently reliable to justify discarding an answer that is already correct. In the tested setting, executable and structural verification did not provide a sufficiently favorable safeguard against this replacement risk.

This negative result is bounded. The experiments use the Spider cross-schema Text-to-SQL workload and `llama3.2:1b`; the verification gate does not perform semantic equivalence checking or employ a stronger independent reasoning verifier. Consequently, the findings do not establish that stronger models, stronger verifiers, different datasets, or alternative evidence policies would exhibit the same boundary.

The practical implication is that analytical agents should treat replacement as a higher-authority action than investigation. A defensible architecture should preserve the incumbent unless a challenger satisfies an independently justified replacement criterion, while recording the evidence, policy decision, verification outcome, provenance, cost, and resulting action for later audit. The Defensibility Layer developed in this work provides an architectural mechanism for preserving that evidence, but does not by itself establish regulatory compliance or production governance.

The principal research boundary established by this study is therefore concise: **an agent can have enough evidence to know that something may be wrong without having enough evidence to safely change the answer**. Future work should focus on stronger semantic verification, calibrated replacement authorization, selective prediction, and evaluation under governed enterprise workloads rather than extending the present routing mechanism without resolving the observed harm–rescue asymmetry.

## 7. Threats to Validity

**Incumbent weakness.** P0 is only approximately 24.6% accurate. This limits absolute performance claims. The paired harm/rescue analysis remains informative because every policy is evaluated on the same cases.

**Small model.** The use of `llama3.2:1b` limits generalization to stronger models.

**Verification strength.** The gate is weaker than recent multi-stage verifiers. The result therefore bounds the tested mechanism rather than verification as a field.

**Benchmark transfer.** Spider is not an enterprise deployment benchmark.

**Holdout ordering.** The historical held-out-schema execution preceded complete development aggregation. It is therefore reported as locked observational corroboration rather than fully prospective confirmation.

**Post-hoc diagnostics.** Diagnostic models were used for mechanism understanding only. They did not become part of the P6-IP decision rule or tune the held-out partition.

**Multiple comparisons.** The primary P6-IP comparison is paired and prespecified. Additional analyses are treated as supporting diagnostics rather than independent discovery claims.

## 8. Reproducibility and Data Availability

The public Spider benchmark and research code required for the reported analyses are maintained in the project repository. The official evaluator is pinned to commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`. P6-IP was executed in GitHub Actions with local Ollama inference; paid/Azure inference was not used.

The development artifact contains 1,034 cases and the locked held-out-schema partition contains 254 cases. Runtime traces, decision records, provenance manifests, statistical analysis scripts, tests, and workflow definitions are retained in the repository or associated research artifacts where applicable.

The research chain is anchored to repository history rather than a mutable benchmark result. Readers reproducing the work should verify the cited commits, workflow run identifiers, evaluator version, and artifact manifests against the repository.

**Data availability:** The Spider dataset is publicly available from its original distribution. Project-specific derived traces and analysis artifacts are maintained with the repository subject to repository and artifact availability constraints.

## 9. Code Availability

The complete research implementation is maintained in the public GitHub repository:

**Repository:** `todkarsant/Enterprise-Analytics-Copilot`  
**Research manuscript branch:** `research/paper-lit-integration`  
**Canonical manuscript:** `paper/PROJECT1_JAI_FINAL_MANUSCRIPT.md`  
**Current immutable manuscript anchor before this reader-focused revision:** commit `01aababc52e0036a22ececf83faec3d12e2834d2`  
**Reproducibility map:** `docs/PROJECT1_REPRODUCIBILITY_MAP.md`

The reproducibility map records the frozen P0–P5 baseline, P5R mechanism-forensics run, P6-IP design and controlled run, official evaluator commit, P0 post-hoc recomputation, analysis-repair commits, decision-record provenance, and research-state controls. It is the primary routing document for reproducing the research chain and should be read together with the manuscript rather than relying on a mutable branch alone.

The final submission copy will be anchored to its own immutable commit after the plagiarism/originality stage and final numerical audit. This separation ensures that the version submitted to JAI can be identified independently of subsequent repository development.

## 10. Funding

**Funding:** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## 11. Declaration of Competing Interest

**Competing interests:** The authors declare that they have no competing financial or personal interests that could have influenced this work.

## 12. Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

During preparation of this manuscript, the authors used OpenAI ChatGPT to assist with language editing, structural revision, research organization, and preparation of publication-oriented text. The authors reviewed and edited the resulting material and take full responsibility for the accuracy, integrity, and final content of the manuscript.

## 13. Author Contributions

**Santosh Sadashiv Todkar:** Conceptualization; Methodology; Software; Investigation; Formal analysis; Data curation; Visualization; Writing – original draft; Project administration; and overall experimental execution and research coordination.

**Digvijay Bhosale:** Validation; Writing – review & editing; review of experimental findings; and contribution of insights concerning interpretation and validation of the experimental findings.

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

[35] M. Tritto, G. Farano, D. Di Palma, G. Rossiello, D. Subramanian, F. Narducci, and T. Di Noia, “GradeSQL: Outcome reward models for intelligent Text-to-SQL generation from LLMs,” Journal of Intelligent Information Systems, 2026, https://doi.org/10.1007/s10844-026-01071-6.

[36] S. Gómez Álvarez, A. Mozo Quesada, T. Navarro, S. Gálvez Rojas, and F. López Valverde, “Multi-Agent debate system based on large language models: structured deliberation and validation in satellite communications,” Journal of Intelligent Information Systems, 2026, https://doi.org/10.1007/s10844-026-01086-z.

[37] B. Gülmez, “Code generation with large language models: a survey from neural program synthesis to autonomous software development,” Applied Intelligence, vol. 56, Art. 200, 2026, https://doi.org/10.1007/s10489-026-07230-0.

[38] X. Li, S. Peng, S. Yada, S. Wakamiya, and E. Aramaki, “GenKP: generative knowledge prompts for enhancing large language models,” Applied Intelligence, vol. 55, Art. 464, 2025, https://doi.org/10.1007/s10489-025-06318-3.

[39] T. R. McIntosh, T. Susnjak, N. Arachchilage, T. Liu, D. Xu, P. Watters, and M. N. Halgamuge, “Inadequacies of Large Language Model Benchmarks in the Era of Generative Artificial Intelligence,” IEEE Transactions on Artificial Intelligence, vol. 7, no. 1, pp. 22–39, 2026, https://doi.org/10.1109/TAI.2025.3569516.

[40] C. N. Hang, P.-D. Yu, and C. W. Tan, “TrumorGPT: Graph-Based Retrieval-Augmented Large Language Model for Fact-Checking,” IEEE Transactions on Artificial Intelligence, vol. 6, no. 11, pp. 3148–3162, 2025, https://doi.org/10.1109/TAI.2025.3567369.

## Submission-control note

This version is intentionally **single-column and plagiarism-check friendly**. It is not yet the journal's final production layout. After the plagiarism/originality check, the manuscript should be transferred into the current JAI/Elsevier editable submission format. At that stage, the flowcharts above should be converted into publication-quality figures, and figures/tables, biographies/photos, pagination, and the final reference audit should be completed.
