# Changelog

## 0.2.3

- Fixed SQL guard rejection of valid SELECT aliases used in ORDER BY/GROUP BY/HAVING.
- Added regression tests for alias handling.
- Added regression coverage for unknown columns and mutation rejection.

## 0.2.2

- Isolated pytest from the developer's `.env` by forcing the Mock LLM provider.
- Added deterministic API assertions for the mock provider.
- Added request validation coverage.
- Documented test execution from the repository root.

## 0.2.1

- Added robust Ollama JSON parsing and deterministic answer fallback.
- Improved relative-date SQL guidance.
