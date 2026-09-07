# Project 1 Research Experiment Contract

## Status

**Phase:** Pre-implementation contract freeze  
**Project:** Adaptive Analytical Execution under Uncertainty  
**Repository:** Enterprise-Analytics-Copilot  
**Date:** 2026-09-07

This document freezes the experimental contract before implementing the proposed policy. The purpose is to prevent post-hoc changes to baselines, metrics, datasets, or stopping rules after results are observed.

## Research question

> Can an evidence-dependent analytical execution policy improve the reliability-constrained cost/latency frontier of enterprise data agents relative to fixed execution paths and strong post-evidence cascade baselines?

This is an empirical question. No algorithmic novelty is assumed.

## Primary falsification test

Compare **P5 Post-Evidence Cascade** against **P6 Heterogeneous Evidence-Dependent Policy** at matched reliability targets on held-out schemas/workloads.

P6 is not considered successful merely because it has higher raw accuracy. The primary claim requires a lower cost and/or latency at a pre-specified reliability target, without using oracle information.

If P6 does not improve the frontier after accounting for all policy overhead, the proposed research contribution is considered unsupported.

## Policies

### P0 Always-LLM

Every eligible question follows the LLM generation path, subject only to mandatory safety/governance validation.

### P1 Deterministic-only

Only deterministic handlers/plans are permitted. Unsupported questions abstain rather than invoking an LLM.

### P2 Static Hybrid

Known deterministic intents use deterministic execution; all other questions use the baseline LLM path.

### P3 Query-Only Complexity Router

The route is selected from question-time features only. No post-retrieval or post-execution evidence may influence the initial decision.

### P4 Query-Only Confidence Router

A pre-execution confidence model determines whether to use a cheap or expensive path. The model may not consume evidence produced after the routing decision.

### P5 Post-Evidence Cascade

A strong cheapest-first cascade may inspect intermediate evidence and escalate to more expensive computation. It must be implemented as a serious baseline, not a deliberately weak strawman.

### P6 Heterogeneous Evidence-Dependent Policy

The policy may select among heterogeneous analytical actions based on the current state and accumulated evidence:

- retrieve_schema
- retrieve_examples
- generate_sql
- deterministic_execute
- execute_sql
- verify_sql
- repair_sql
- clarify
- agentic_escalation
- abstain

The action policy must account for cost/latency already spent and must not inspect gold labels, reference SQL, or hidden benchmark metadata at inference time.

## State contract

At step `t`, the policy may consume:

- user question
- conversation history available to the system
- retrieved schema/context
- retrieved examples
- generated SQL and structural features
- validation results
- execution errors/results
- verification outputs
- ambiguity signals
- governance/policy checks
- elapsed latency
- accumulated token/tool cost
- remaining configured budget
- prior actions and outcomes

Gold SQL, gold answers, hidden labels, benchmark IDs that encode difficulty, and post-hoc evaluator outputs are prohibited from the policy state.

## Primary outcomes

### Reliability

Report separately:

1. SQL validity
2. semantic correctness
3. result correctness
4. answer/evidence correctness
5. governance compliance
6. ambiguity handling
7. unanswerable handling

Do not collapse these into a single score without publishing the components.

### Efficiency

- total token count
- LLM calls
- tool/action calls
- estimated monetary cost
- deterministic compute time where measurable
- LLM time
- database time
- end-to-end latency
- P50/P95 latency

### Policy behavior

- escalation rate
- clarification rate
- abstention rate
- unnecessary escalation rate
- action distribution
- average actions per query
- cost spent before final decision

## Primary metric

For each reliability target `R` in `{0.90, 0.95, 0.97, 0.99}`:

`C(R) = minimum observed mean cost among policies whose held-out reliability is >= R.`

Secondary frontier views should report latency and coverage at the same reliability target.

A lower `C(R)` is not evidence of superiority if reliability is not statistically compatible with the target or if the policy has materially different coverage due to abstention. Coverage and abstention must therefore be reported alongside the frontier.

## Evaluation splits

The benchmark must separate:

- development/tuning
- validation/model-selection
- held-out test
- unseen-schema test
- where feasible, unseen-domain test

No policy threshold may be tuned on the final test set.

## Required workload strata

1. deterministic/simple aggregation
2. schema ambiguity
3. semantic ambiguity
4. wrong grain/join risk
5. misleading premise
6. unanswerable request
7. authorization/governance constraint
8. multi-step analytical reasoning
9. multi-turn context dependence
10. execution-error/repair cases

Each stratum must contain enough examples to estimate failure rates with useful confidence intervals; the final sample size will be justified before the main run.

## Mandatory baselines against prior art

The implementation must include a genuine post-evidence cascade baseline because recent work demonstrates that the need for expensive computation can become visible only after cheaper evidence-producing stages.

A model-only routing comparison is insufficient.

## Ablations

At minimum:

- remove verification
- remove clarification
- remove deterministic execution
- remove retrieval
- remove execution-result features
- remove uncertainty features
- remove accumulated-cost features
- restrict P6 to model escalation only
- restrict P6 to fixed action ordering
- remove unseen-schema transfer

The key ablation is to determine whether heterogeneous action selection—not merely additional computation—causes the gain.

## Statistical analysis

For primary test comparisons:

- report paired per-query outcomes where applicable
- bootstrap confidence intervals for cost, latency, and reliability differences
- use paired permutation/bootstrap tests rather than treating repeated queries as independent when the same query is evaluated under multiple policies
- report effect sizes, not only p-values
- report multiple-comparison correction when making multiple confirmatory claims

No significance threshold will be chosen after observing the results.

## Cost accounting rules

All policy overhead counts.

This includes:

- router inference
- verifier inference
- clarification turns when simulated/evaluated
- retrieval calls
- SQL generation
- repair calls
- agentic escalation

A policy cannot claim efficiency by excluding its own routing/verifier cost.

If actual provider pricing is unavailable or variable, report token counts and latency as primary reproducible measures and label monetary cost as an estimate.

## Oracle prohibitions

The policy must not receive:

- gold SQL
- gold result
- reference answer
- known benchmark difficulty label
- evaluator score
- human correctness judgment generated after execution
- test-set-specific threshold

Any experiment using such information must be labeled an oracle/diagnostic experiment and excluded from the primary comparison.

## Reviewer attack checklist

Before claiming success, attempt to falsify the result through:

- unseen schemas
- unseen domains
- alternate model/provider
- alternate database backend where feasible
- deterministic shortcut removal
- equal-compute comparison
- equal-reliability comparison
- threshold sensitivity
- bootstrap confidence intervals
- cost-accounting audit
- abstention/coverage audit
- failure-mode breakdown
- repeated runs for stochastic components

## Claim discipline

Allowed claim form:

> On the evaluated benchmark and under the stated policy/cost assumptions, P6 achieved X at matched reliability compared with Y.

Disallowed claim form unless independently established:

> P6 is a generally superior architecture for enterprise AI agents.

The study is not permitted to claim universal optimality, general enterprise deployment performance, or algorithmic novelty from benchmark results alone.
