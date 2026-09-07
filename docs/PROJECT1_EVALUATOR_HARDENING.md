# Project 1 — Evaluator and Baseline Hardening

## Purpose

The first Spider 1.0 development run exposed three methodological problems:

1. the primary correctness metric was a custom row-set comparison rather than the official Spider evaluator;
2. P1/P2/P3/P4/P5 used an empty deterministic mapping, so the policy family did not test the intended deterministic component;
3. evaluator-only gold SQL was too close to the system result contract and was not explicitly separated from policy execution.

This branch fixes those issues before any P6 claim is considered.

## Primary metric

The benchmark now loads the official `taoyds/spider` evaluator from a pinned external commit:

`b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`

The official Spider execution-equivalence implementation is the **primary execution metric**. The previous row-set comparison remains only as `secondary_custom_results` for diagnostics.

Spider's project documentation states that Test Suite Accuracy is its official leaderboard metric. This branch therefore does **not** label ordinary Spider execution accuracy as Test Suite Accuracy. Test-suite evaluation requires the separate test-suite databases; that additional metric will be enabled only when those databases are supplied and version-pinned.

## Deterministic baseline

The benchmark no longer defaults to an empty question-to-SQL mapping.

`RuleBasedDeterministicSolver` is a frozen, schema-aware baseline that:

- reads only the database schema;
- uses lexical evidence from the natural-language question;
- supports conservative single-table count/aggregate/direct/order patterns;
- abstains on unsupported or ambiguous patterns;
- never reads Spider gold SQL;
- never reads evaluator outcomes;
- has no question-to-gold lookup table.

This is intentionally a **weak but auditable baseline**, not a claim of strong deterministic Text-to-SQL performance.

## Evaluation boundary

For every trace:

`question + schema -> policy -> generated SQL -> database execution`

is completed before evaluator access.

Only after the policy trace is complete does the evaluator compare the generated SQL with the gold SQL. The policy cannot inspect:

- gold SQL;
- gold execution results;
- correctness labels;
- evaluator scores;
- Spider hardness labels.

## Required benchmark outputs

The artifact records:

- `official_spider_execution`: primary metric;
- `secondary_custom_results`: diagnostic metric only;
- per-trace `official_execution_correct`;
- per-trace `custom_execution_correct`;
- action trace, latency, LLM calls and modeled action cost;
- dataset checksum manifest;
- deterministic baseline declaration.

## Test Suite Accuracy

Do not report Test Suite Accuracy from the ordinary Spider SQLite databases. The official test-suite evaluator uses separate test-suite databases. A future benchmark may add those databases as an explicit, versioned dependency.

## Falsification gate

No P6 result is research evidence until:

1. P0-P5 are rerun with the primary evaluator;
2. P1 uses the frozen rule-based baseline;
3. the benchmark artifact is checksumed and reproducible;
4. actual latency/token/cost telemetry is retained;
5. P5 is characterized as the strongest post-evidence reference;
6. paired uncertainty analysis is run;
7. unseen-schema transfer is evaluated.

If P6 does not improve the reliability-constrained cost/latency frontier over P5, the research claim is reframed rather than rescued through metric selection.
