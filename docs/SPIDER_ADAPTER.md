# Spider 1.0 adapter

This branch adds the first real-benchmark ingestion layer for Project 1. It is intentionally **not** a model benchmark result.

## Source and split

Use the corrected Spider 1.0 release linked by the Yale-LILY task page:

- Source: https://yale-lily.github.io/spider
- Benchmark: Spider 1.0
- Split: `dev.json`
- License: CC BY-SA 4.0
- Local layout expected:

```text
data/spider/
  dev.json
  tables.json
  database/
    <db_id>/<db_id>.sqlite
```

The upstream Spider repository states that `dev.json` contains the natural-language question, `db_id`, and gold `query`, while `tables.json` contains schema, key, and foreign-key metadata. The upstream evaluation tooling supports exact/component and execution evaluation. This project does not vendor the dataset.

## Reproducibility

Run:

```bash
python scripts/validate_spider.py --root data/spider --write-manifest artifacts/spider_manifest.json
```

The manifest records SHA-256 and byte size for `dev.json`, `tables.json`, and every SQLite database. This makes the benchmark input auditable without committing the benchmark data to Git.

## Evaluation boundary

`research/spider_adapter.py` exposes three separate surfaces:

1. `cases()` — question, database id, and gold SQL for the evaluator.
2. `schemas()` — schema metadata available to a policy/runtime.
3. `execute()` — read-only SQLite execution for candidate SQL.

A policy must never receive `gold_sql`. Gold SQL is evaluator-only metadata.

The adapter does **not** claim execution accuracy, policy superiority, or P6 evidence. A prediction-producing runtime and the P0–P5 experiment runner must be connected before any research result is recorded.

## Why Spider 1.0 first

Spider is a controlled first external benchmark because it is cross-domain and requires schema generalization, while its SQLite databases are practical for local reproducible execution. Spider 2.0 is a more realistic follow-on benchmark and should be treated separately rather than silently mixed with Spider 1.0 results.
