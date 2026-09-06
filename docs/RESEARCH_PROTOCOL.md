# Project 1 Evaluation Protocol

## Objective

Establish a reproducible evaluation protocol for adaptive analytical execution before collecting confirmatory results.

## Experimental phases

### Phase A — Harness validation

Verify that the benchmark schema, action logging, evaluator, cost accounting, and policy interfaces work correctly on deterministic fixtures.

No research conclusions are drawn from Phase A.

### Phase B — Baseline characterization

Run P0-P5 on development/validation workloads. Tune only where the baseline specification permits tuning. Freeze configurations.

### Phase C — Primary comparison

Run P5 and P6 on the held-out test set with frozen configurations.

### Phase D — Generalization

Run frozen policies on unseen schemas and, where available, unseen domains.

### Phase E — Mechanism ablation

Test whether P6 gains are attributable to heterogeneous evidence-dependent action selection rather than simply more calls or more computation.

## Randomness

Record all seeds and model/provider versions. For stochastic systems, use repeated runs where feasible and report variability rather than a single lucky run.

## Cost normalization

Primary efficiency measures:

1. input tokens
2. output tokens
3. number of model calls
4. total action/tool calls
5. wall-clock latency
6. component latency

Monetary cost is secondary unless provider pricing is fixed and reproducible. Any price table must record the source and date.

## Statistical reporting

For every primary comparison:

- paired per-case difference
- point estimate
- bootstrap 95% confidence interval
- effect size
- sample count
- per-stratum result

When testing multiple confirmatory hypotheses, predefine the correction procedure before final analysis.

## Reliability targets

Primary frontier targets:

- 90%
- 95%
- 97%
- 99%

If a target cannot be reached by a policy, report it as unavailable rather than extrapolating.

## Coverage

Coverage is:

`non-abstained, validly handled cases / total cases`

A policy may not improve its reliability score merely by abstaining on difficult cases without the corresponding coverage impact being visible.

## Human evaluation

If answer-level correctness cannot be determined deterministically for a workload stratum, use blinded human evaluation with a documented rubric. Human evaluators must not know the policy identity where feasible.

## Reproducibility package

A confirmatory release must include:

- benchmark version/hash
- policy configurations
- code commit
- model/provider identifiers
- environment/dependency lock
- seeds
- raw run summaries
- aggregate analysis scripts
- statistical analysis output
- failure taxonomy

## Stop rules

Do not proceed to a paper claim if:

- the evaluator leaks labels into policy execution;
- test-set tuning occurred;
- costs are incompletely accounted for;
- P5 is materially weaker than a reasonable implementation should be;
- reliability differences cannot be estimated with meaningful uncertainty;
- P6's advantage disappears under equal-compute or unseen-schema analysis;
- or the result depends on an unreported manual exception.
