# Project 1 — P0–P5 Frozen Evidence Review

**Date:** 2026-09-08  
**Branch:** `research/p1-evaluator-hardening`  
**Workflow run:** `34206500727`  
**Purpose:** Review the completed frozen P0–P5 artifacts before any new benchmark execution or P6 work.

## 1. Artifact integrity

The 12 isolated benchmark artifacts were retrieved and inspected.

- 12/12 chunks present.
- Each chunk contains all six policies P0–P5.
- Development traces: 1,034 cases × 6 policies = 6,204 traces.
- Unseen holdout traces: 254 cases × 6 policies = 1,524 traces.
- No duplicate `(question, db_id, policy)` keys were found within the assembled development or holdout artifacts.
- Timeout/error traces remain in the denominator.
- The pinned official Spider execution result is retained as the primary correctness signal.

## 2. Critical split interpretation

The existing `unseen` artifact is a 254-case holdout consisting of four schemas: `car_1`, `flight_2`, `real_estate_properties`, and `student_transcripts_tracking`.

Those same four schemas are also present in the 1,034-case development artifact. Therefore the current artifacts do **not** support the claim that the 254 cases are an independent unseen-schema test set if the 1,034-case set is treated as the development set.

However, the frozen traces can be partitioned without rerunning inference:

- 16 non-holdout schemas: 780 cases → development partition.
- 4 held-out schemas: 254 cases → unseen-schema partition.

This is the scientifically defensible interpretation only if policy/model decisions were not tuned using the held-out schemas. The manuscript must not describe the full 1,034-case run as a disjoint development set plus the 254-case unseen set.

## 3. Official execution accuracy

### Full 1,034-case Spider run

| Policy | Correct | Accuracy | Coverage | Mean cost units | Median latency (ms) | P95 latency (ms) |
|---|---:|---:|---:|---:|---:|---:|
| P0 | 254 | 24.56% | 98.16% | 0.2691 | 2000.85 | 5603.12 |
| P1 | 0 | 0.00% | 63.44% | 0.0517 | 120.00 | 134.88 |
| P2 | 256 | 24.76% | 97.87% | 0.2687 | 1540.36 | 4817.35 |
| P3 | 256 | 24.76% | 97.87% | 0.2687 | 1541.21 | 4817.57 |
| P4 | 20 | 1.93% | 69.15% | 0.0849 | 120.83 | 3087.71 |
| P5 | 123 | 11.90% | 81.14% | 0.2439 | 1279.52 | 11567.33 |

No tested policy reaches the 90% reliability target. This is a negative result, not a reason to lower the target.

## 4. Strongest-comparator result: P5 vs P0

On all 1,034 cases:

- P0 correct: 254
- P5 correct: 123
- P0-only correct: 158
- P5-only correct: 27
- Accuracy delta (P5 − P0): −12.67 percentage points.

On the disjoint 780-case development partition:

- P0: 193/780 = 24.74%
- P5: 91/780 = 11.67%
- P0-only: 120
- P5-only: 18
- Accuracy delta: −13.08 percentage points.

On the 254-case held-out schema partition:

- P0: 61/254 = 24.02%
- P5: 32/254 = 12.60%
- P0-only: 38
- P5-only: 9
- Accuracy delta: −11.42 percentage points.

Thus P5 is not merely failing to improve P0; it materially regresses against the mandatory strongest comparator on both partitions.

## 5. P5 characterization

P5's most frequent paths include:

- `retrieve_schema → deterministic_execute → abstain` — 304 cases
- `retrieve_schema → deterministic_execute → generate_sql → execute_sql → abstain` — 217 cases
- `retrieve_schema → abstain` — 189 cases
- `retrieve_schema → deterministic_execute → generate_sql → execute_sql → repair_sql → execute_sql → verify_sql → abstain` — 101 cases

P5 produced 123 official-correct cases and 911 incorrect cases on the full run. The evidence therefore does not support presenting P5 as a successful reliability-constrained cascade.

## 6. Research decision

P6 should **not** be implemented or benchmarked merely to recover the hypothesis. The frozen evidence currently supports a negative/inconclusive boundary result:

> Under the tested Spider/SQLite setup and `llama3.2:1b`, neither the fixed policies nor the post-evidence cascade achieves the predefined 90% reliability target, and the post-evidence cascade is substantially worse than Always-LLM on official execution accuracy.

The next research work should therefore be:

1. preserve the frozen P0–P5 evidence;
2. formalize the disjoint 16-schema/4-schema interpretation;
3. verify whether any P0–P5 policy parameter or threshold was tuned using the four held-out schemas;
4. perform publication-grade paired statistics, confidence intervals, cost/latency effect sizes, timeout sensitivity, and failure taxonomy;
5. decide whether a prospective P6 has a scientifically defensible unresolved gap rather than a performance-recovery motivation;
6. if no defensible gap remains, reframe the contribution around the empirical boundary/failure modes rather than forcing a positive adaptive-routing claim.

No new inference run is required at this stage.
