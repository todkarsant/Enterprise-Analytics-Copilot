# Changelog

## 0.2.4

- Added physical table alias resolution in the SQL guard.
- Added detection/rejection of unnecessary self-joins for the current one-table schema.
- Strengthened Ollama SQL-generation instructions for top-store aggregations.
- Added regression tests for valid aliases and self-join rejection.

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
