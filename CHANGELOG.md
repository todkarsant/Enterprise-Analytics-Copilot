# Changelog

## 0.2.7

- Added `analytical_planner.py` for supported diagnostic/comparison questions.
- Added end-to-end `Why did sales decline?` workflow.
- Added latest-vs-previous-period sales comparison.
- Added store-level contributor analysis.
- Added evidence-grounded deterministic analytical answers.
- Deterministic intents no longer spend an LLM call on answer summarization.
- Added structured analytical results to the API response.
- Replaced deprecated FastAPI startup event with lifespan.
- Improved Streamlit error presentation so raw FastAPI error JSON is not the primary user-facing message.
- Added `EVOLUTION.md` and architecture decision records.
- Expanded evaluation script and regression tests.
- Preserved `llama3.2:1b` as a baseline rather than changing models without benchmark evidence.

## 0.2.6

- Added a conservative deterministic Intent Planner before LLM SQL generation.
- Added high-confidence templates for top stores by sales/orders, regional sales, last-month total sales, promotion spend, and advertising spend.
- Added planner observability fields: `planner_used` and `intent`.

## 0.2.5

- Fixed false-positive self-join detection for valid physical table aliases.

## 0.2.4

- Added physical table alias resolution and unnecessary self-join detection.

## 0.2.3

- Fixed SQL guard rejection of valid SELECT aliases.

## 0.2.2

- Isolated pytest from developer `.env` by forcing Mock provider in tests.

## 0.2.1

- Added robust Ollama JSON parsing and deterministic answer fallback.
