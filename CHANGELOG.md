# Changelog

## 0.2.6

- Added a conservative deterministic Intent Planner before LLM SQL generation.
- Added high-confidence templates for top stores by sales/orders, regional sales,
  last-month total sales, promotion spend, and advertising spend.
- Added planner observability fields: `planner_used` and `intent`.
- Added planner regression tests.
- Unknown/ambiguous questions continue to the LLM path.

## 0.2.5

- Fixed false-positive self-join detection for valid physical table aliases.
- Added regression coverage for `store_week AS sw`.

## 0.2.4

- Added physical table alias resolution.
- Added unnecessary self-join detection for the single-table demo schema.
- Strengthened Ollama SQL-generation instructions for top-store aggregation.

## 0.2.3

- Fixed SQL guard rejection of valid SELECT aliases.
- Added regression tests for alias handling.

## 0.2.2

- Isolated pytest from the developer's `.env` by forcing the Mock LLM provider.
- Added deterministic API assertions for the mock provider.
- Added request validation coverage.

## 0.2.1

- Added robust Ollama JSON parsing and deterministic answer fallback.
- Improved relative-date SQL guidance.
