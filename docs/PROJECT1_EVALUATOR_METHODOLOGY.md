# Project 1 — Spider Evaluator Methodology

## Decision

The pinned official Spider execution evaluator is the **primary correctness metric** for benchmark claims. The repository's row-set comparison is retained only as a **secondary diagnostic**.

We do not replace or override the official score when the two metrics disagree.

## Forensic finding from Run #44

Run #44 exposed several cases where the secondary row-set comparison returned `True` while the official Spider execution metric returned `False`.

Examples included equivalent-looking aggregate queries such as:

```sql
SELECT COUNT(Singer_ID) FROM singer
```

versus a gold query using a different SELECT value unit, and queries that produced the same apparent row set but differed in parsed SELECT expressions.

This is **not evidence that the pinned evaluator is broken**.

The pinned evaluator's `eval_exec_match` constructs result maps keyed by parsed SELECT value units and compares the values associated with those keys. The evaluator therefore evaluates execution results in the context of the predicted and gold SELECT expressions rather than treating the complete unordered row set as the sole equivalence relation.

Reference: pinned `taoyds/spider` commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`, `evaluation.py`.

## Why the secondary metric is retained

Row-set equality is useful for diagnosis because it can reveal cases where two executable SQL statements produce the same rows despite differing SQL structure. However, it is intentionally permissive and is not a substitute for the benchmark's declared primary metric.

The benchmark payload therefore records:

- `official_spider_execution`: primary research metric
- `secondary_custom_results`: diagnostic row-set metric
- per-trace `official_execution_correct`
- per-trace `custom_execution_correct`

## Forensic classification

The benchmark now produces a separate evaluator-forensics artifact. A disagreement is classified as:

- `agreement`
- `official_stricter_than_rowset_diagnostic`
- `official_match_rowset_diagnostic_disagrees`

The forensic artifact may include SQL and result-shape details for human inspection, but those details are not fed back into policy execution or routing.

## Research integrity boundary

Gold SQL is evaluator-only. Policy code receives the question and schema, but never the reference SQL or reference result. The forensic comparison runs **after** policy execution.

No benchmark tuning may use individual forensic findings to optimize against the development smoke set and then report those tuned results as held-out evidence.

## Consequence for Project 1

The earlier phrase "evaluator discrepancy" should be interpreted as **metric disagreement**, not an evaluator defect.

The current methodology is therefore:

1. keep the pinned official Spider execution evaluator as primary;
2. retain row-set equality only as a diagnostic;
3. record metric disagreements separately;
4. inspect systematic disagreement before making scientific claims;
5. preserve the dataset, evaluator commit, split, and seeds for reproducibility;
6. do not run the 1,034-case characterization benchmark until this methodology is validated by CI.
