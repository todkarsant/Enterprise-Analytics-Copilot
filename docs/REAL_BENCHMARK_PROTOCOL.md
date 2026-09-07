# Real Benchmark Protocol — Project 1

## Status

**Pre-P6. No P6 implementation or superiority claim is permitted by this protocol.**

The deterministic `research/fixtures.py` experiment is a mechanics test only. It is not evidence for research conclusions.

## Primary external benchmark

The first external benchmark is **Spider 1.0 development data with execution-based evaluation**.

Official sources:

- Spider task page: https://yale-lily.github.io/spider
- Spider code/evaluation: https://github.com/taoyds/spider

Spider contains cross-domain databases and requires generalization to unseen database schemas. The official project page reports 10,181 questions, 5,693 unique SQL queries, and 200 databases. The official repository provides the evaluation implementation.

The benchmark data itself is not vendored into this repository.

## Why Spider first

Spider gives us a public, reproducible baseline for SQL correctness before adding enterprise-specific dimensions. It is intentionally not presented as a complete enterprise-data-agent benchmark. Later experiments may add BIRD, conversational/ambiguity benchmarks, governance/RBAC cases, and enterprise-style workloads.

## Dataset handling

A benchmark run must record:

- dataset name and version/commit
- split name
- database bundle checksum
- question-file checksum
- evaluator version/commit
- model/provider identifier, if applicable
- temperature and generation settings, if applicable
- policy version
- action-cost configuration
- random seed
- run timestamp

The dataset and database files remain external inputs. No benchmark result is valid unless the exact input checksums are recorded.

## Evaluation layers

Each policy run must preserve two distinct layers:

### 1. System outcome

Observed without access to the gold answer while the policy executes:

- generated SQL
- SQL validity
- execution success/failure
- execution result
- action sequence
- tool/LLM calls
- latency
- token usage where available
- cost accounting
- termination reason

### 2. Evaluator outcome

Computed only after execution from the benchmark reference:

- execution correctness
- exact-match where supported by the official evaluator
- coverage
- governance outcome when a governed benchmark is used

The policy must never receive the gold SQL, gold result, or evaluator-only labels during execution.

## Baselines required before P6

The real benchmark must characterize, at minimum:

- P0 Always-LLM
- P1 Deterministic-only
- P2 Static Hybrid
- P3 Query-only Complexity Router
- P4 Query-only Confidence Router
- P5 Post-Evidence Cascade

P5 is the strongest pre-P6 reference and must be treated as a serious competitor, not a strawman.

## Primary comparison

The research question is evaluated as a constrained efficiency comparison:

> Minimize expected analytical cost subject to a predefined reliability target.

Primary reliability targets:

- 0.90
- 0.95
- 0.97
- 0.99

A target is reported as **unreachable** when no policy configuration reaches it on the evaluated split. No extrapolation is allowed.

Primary efficiency measures:

- mean cost per covered query
- median and P95 latency
- total LLM/tool calls
- escalation rate
- unnecessary escalation rate
- missed-escalation rate
- coverage
- execution correctness

## Required reporting

Every policy result must include per-example records sufficient to reconstruct:

`question -> initial state -> action sequence -> intermediate evidence -> terminal outcome -> evaluator outcome -> cost/latency`

Aggregate tables must not replace per-example traces.

## Fairness constraints

All policies must use:

- the same dataset split
- the same model/provider when a model is required
- the same maximum generation budget
- the same database execution environment
- the same action-cost accounting
- the same timeout policy
- the same evaluation code

Thresholds must be selected on a calibration/development split and frozen before the final comparison. The final comparison must not tune thresholds against its own outcomes.

## Required ablations after P6 exists

If and only if P6 survives the pre-P6 characterization, evaluate:

1. P6 without verification evidence
2. P6 without execution-result features
3. P6 without ambiguity features
4. P6 without accumulated-cost features
5. model-only escalation instead of heterogeneous actions
6. fixed action ordering
7. equal-compute/random escalation control
8. unseen-schema transfer

## Falsification rule

The central claim fails if P6 does not improve the reliability-constrained cost/latency frontier over P5 under matched evaluation conditions, or if the observed gain disappears under the required ablations or unseen-schema evaluation.

If P5 matches or beats P6, the project will report that result and reframe the contribution rather than claiming novelty.

## Current gate

- [x] Harness tests pass
- [x] CI passes on the research branch
- [x] Synthetic mechanics fixture explicitly labeled non-evidence
- [ ] External benchmark adapter
- [ ] P0-P5 external benchmark characterization
- [ ] P5 challenge/falsification
- [ ] P6 implementation
- [ ] P6 ablations and replication
