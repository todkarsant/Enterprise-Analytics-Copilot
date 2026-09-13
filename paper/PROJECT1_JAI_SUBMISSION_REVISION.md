# Project 1 — JAI Submission Revision

**Proposed title:** When Evidence Is Not Enough: Replacement Decisions in Analytical AI Agents

## Abstract

AI agents can retrieve evidence, generate and execute SQL, and invoke additional reasoning when an analytical task appears difficult. In enterprise analytics, however, detecting risk is not the same as knowing when an answer should be changed. This study examines whether evidence that justifies further investigation is also sufficient to authorize replacement of an existing answer.

We separate three decisions: predicting that an answer may be wrong, deciding whether additional computation is justified, and authorizing replacement. We evaluate frozen baseline policies, perform mechanism forensics, and test an incumbent-preserving policy that intervenes using decision-time evidence and replaces the incumbent only after SQL validity, execution, and structural checks.

On 1,034 cross-schema Text-to-SQL cases, the incumbent achieves approximately 24.6% execution accuracy, versus 22.6% for the tested replacement policy, while mean cost increases by approximately 25.8%. Among development cases selected for intervention, 33.87% of correct incumbent answers were harmed, whereas only 0.75% of incorrect incumbent answers were rescued. The held-out-schema partition shows the same directional pattern.

The result establishes a practical reliability boundary: **evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement**. The study therefore separates risk detection, intervention, replacement authorization, and auditability as distinct controls for analytical AI systems.

**Keywords:** Analytical agent; Text-to-SQL; Selective prediction; Verification; Auditability

## Title and framing rationale

The proposed title is deliberately shorter than the current “When Evidence Is Not Enough: Reliability Boundaries of Evidence-Driven Analytical Agents.” It identifies the actual scientific object—replacement decisions—without claiming a universal reliability boundary. It also avoids abbreviations and formulae, consistent with the Journal of Automation and Intelligence guidance that titles should be concise and informative.

## 1. Core message to readers

The paper should be understood in one sentence:

> **An AI system may have enough evidence to justify looking again without having enough evidence to justify changing the answer.**

This is the bridge between the research result and enterprise AI reliability. The paper is not proposing another routing heuristic. It tests how much decision authority can safely be assigned to evidence available during execution.

## 2. Recommended introduction framing

Modern analytical agents do more than generate answers. They decide when to retrieve information, execute tools, verify results, spend additional computation, ask for clarification, or escalate. These capabilities are established features of agentic systems rather than, by themselves, a research contribution.

The harder enterprise problem is **decision authority**. When an agent observes evidence suggesting that an answer may be wrong, should it merely investigate further, or should it be allowed to replace the answer it already has?

This study separates three decisions:

```text
RISK
Is the current answer suspicious?

        ↓

INTERVENTION
Is additional computation justified?

        ↓

REPLACEMENT
Is the challenger strong enough to discard the incumbent?
```

A fourth concern is operational rather than predictive:

```text
AUDITABILITY
Can the decision later be reconstructed and examined?
```

The central proposition is:

> **Evidence sufficient to justify investigation is not necessarily evidence sufficient to authorize replacement.**

The experimental question is narrower:

> **Under a cross-schema Text-to-SQL workload, can an evidence-triggered incumbent-preserving policy improve the harm–rescue–cost trade-off relative to a frozen incumbent analytical policy?**

The paper does not claim novelty for agentic Text-to-SQL, abstention, adaptive routing, verification, AI auditing, or enterprise semantic governance. Its contribution is the empirical separation of prediction, intervention, and replacement authorization; paired measurement of harm and rescue; and a defensibility-oriented evidence record for reconstructing consequential decisions.

## 3. Literature positioning

The directly verified literature creates three important constraints on the contribution.

### Agentic AI

Nisa et al. describe agentic AI through autonomy, reasoning, tool use, reflection, planning and related capabilities while identifying reliability, alignment, scalability, ethical and deployment challenges. The implication for Project 1 is that autonomous sequential action is established; the unresolved question is how much authority should follow from intermediate evidence.

### Trustworthy decision-making

Song and Zhang emphasize verifiable, robust and safe decision-making with explicit constraints and interpretable pathways. Their work is grounded in physics-informed AI and control, so Project 1 adopts only the general principle that consequential AI decisions require more than predictive capability.

### Text-to-SQL verification

G²SQL demonstrates that verification can be substantially richer than executable or structural checks through a two-stage guided and guarded mechanism with reviewer/observer components. This is a direct limitation on Project 1: the tested verifier is intentionally constrained and cannot be presented as a general solution to Text-to-SQL correctness.

### AI auditing

Birhane et al. distinguish audit activity from effective accountability. Project 1 therefore treats its evidence and provenance records as auditability-supporting infrastructure, not as proof of institutional accountability or legal compliance.

## 4. Experimental result that matters

The frozen benchmark contains 1,034 cases. P0 is correct on approximately 24.6%; P6-IP is correct on approximately 22.6%. P6-IP increases mean cost by approximately 25.8%.

The decisive analysis is paired harm versus rescue:

| Partition | Intervention-eligible | P0-correct eligible | P0-wrong eligible | Harm | Rescue |
|---|---:|---:|---:|---:|---:|
| Development | 330 | 62 | 268 | 21 | 2 |
| Held-out schemas | 91 | 16 | 75 | 5 | 1 |

On development cases, harm is 33.87% among P0-correct interventions, while rescue is 0.75% among P0-wrong interventions. The held-out-schema partition shows the same direction: 31.25% harm versus 1.33% rescue.

The historical holdout execution preceded complete development aggregation and is therefore retained only as locked observational corroboration, not as a fully prospective confirmatory test. No holdout outcome was used for tuning, and the development result alone triggers the predefined stop rule.

## 5. What the experiment establishes

The strongest supported statement is:

> **Under the tested Spider cross-schema setting, decision-time evidence combined with executable and structural verification did not provide a sufficiently favorable harm–rescue trade-off for incumbent replacement.**

In plain language:

> **The system could find reasons to look again, but those reasons were not reliable enough to justify throwing away the current answer.**

This is a conditional empirical result. It does not establish that stronger verifiers, larger models, different enterprise datasets, or other evidence policies would fail.

The observed asymmetry is consistent with the tested evidence features and verification gate failing to reliably discriminate between a wrong incumbent that should be replaced and a correct incumbent that merely exhibits evidence that looks risky.

## 6. Defensibility implication

The negative result separates reliability from auditability.

A benchmark evaluator answers:

> Was the final answer correct?

A defensibility record should additionally support:

> What did the system know when it acted?
>
> What evidence triggered the action?
>
> Which policy rule was applied?
>
> Which verification and authorization controls were used?
>
> What happened, and can the decision be reconstructed later?

The Defensibility Layer therefore records evidence provenance, policy rationale, verification, authorization hooks, outcomes, cost, and reproducibility separately from post-hoc correctness. It does not claim legal compliance or institutional accountability.

## 7. Revised conclusion

The central finding of Project 1 is simple: **an AI system can have enough evidence to justify looking again without having enough evidence to justify changing the answer.**

Starting from a frozen incumbent, P6-IP used decision-time evidence to identify cases for further reasoning and allowed a challenger to replace the incumbent only after executable and structural checks. Under the tested cross-schema Text-to-SQL setting, this mechanism did not improve the incumbent. Accuracy fell from approximately 24.6% to 22.6%, mean cost increased by approximately 25.8%, and the intervention analysis showed substantially more harmful replacements than useful rescues.

Among development cases selected for intervention, 21 of 62 correct incumbent answers were harmed, while only 2 of 268 incorrect incumbent answers were rescued. The held-out-schema partition showed the same directional pattern. The result is therefore not a claim that adaptation or verification is impossible. It is a boundary on the authority assigned to the particular evidence and verification mechanism tested here.

The study consequently separates four questions that should not be collapsed into a single notion of AI confidence:

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

For enterprise AI, this separation matters. A system may be allowed to investigate a suspicious answer without being allowed to replace it automatically. Decision authority should therefore be proportional not merely to the presence of evidence, but to the strength of evidence required for the action being authorized.

The practical research direction is not another routing heuristic. It is to measure how reliably AI systems distinguish risk detection, intervention value, replacement safety, and auditable decision-making across models, domains, and operating conditions.

## 8. JAI Guide for Authors — verified implementation requirements

The current Journal of Automation and Intelligence Guide for Authors was checked directly. The following requirements are material to this manuscript:

1. **Article type:** Full-length Research Article covers original research in control and machine learning. The guide states a nominal 12-page target and a maximum of 20 pages including biographies and photos.
2. **Title:** concise and informative; avoid abbreviations and formulae where possible.
3. **Abstract:** concise and factual; state purpose, principal results, and major conclusions; it must stand alone; references should be avoided.
4. **Keywords:** immediately after the abstract; maximum 6; avoid general/plural terms and multiple concepts.
5. **References:** every in-text reference must appear in the reference list and vice versa. DOI is strongly encouraged. ArXiv should be used only when a published version cannot reasonably be obtained.
6. **Web references:** full URL and access date are required as a minimum.
7. **Data/code:** the journal encourages sharing data, software, code, models, algorithms, protocols and methods and encourages a data-availability statement.
8. **Funding:** funding sources must be identified; where there is no funding, the guide provides a recommended no-specific-grant statement.
9. **Competing interests:** a competing-interests statement is required even when there are none to declare.
10. **Generative AI:** the guide encourages a declaration for generative AI or AI-assisted technologies used in scientific writing, with human oversight and author responsibility.
11. **Review:** the journal uses single-anonymized review and normally sends suitable manuscripts to at least two independent reviewers.

Source: Journal of Automation and Intelligence, Guide for Authors, accessed 14 September 2026: https://www.keaipublishing.com/en/journals/journal-of-automation-and-intelligence/guide-for-authors/

## 9. Pre-submission actions still required

This revision fixes the scientific communication issues identified in the current manuscript: title length, abstract density, missing keywords, and conclusion clarity. Before an actual JAI submission, the complete manuscript must additionally be converted to the journal's required editable submission format/template, checked against the 20-page Research Article limit, and supplied with the required author/affiliation/corresponding-author information, biographies/photos, declarations, figures/tables, and final reference formatting.

The current manuscript should not yet be described as fully JAI-submission-compliant solely because these front/back sections have been revised.
