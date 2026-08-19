# ADR-004 — Deterministic Intent Planner

## Context

A 1B local model repeatedly generated unnecessary SQL complexity for obvious business intents.

## Decision

Recognize high-confidence intents and render SQL deterministically. Use the LLM only for questions outside those patterns.

## Consequences

Positive:
- lower latency for known intents
- zero LLM SQL tokens for known intents
- reproducible SQL
- easier testing

Trade-off:
- planner coverage must remain conservative; incorrect intent classification would be worse than an LLM fallback.
