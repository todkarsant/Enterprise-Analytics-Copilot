# ADR-003 — Bounded Repair Loop

## Context

Some generated SQL is syntactically valid but violates schema/policy checks.

## Decision

Allow a small configurable number of repair attempts and stop rather than looping indefinitely.

## Consequences

Positive:
- controlled failure behaviour
- predictable worst-case LLM usage
- validation remains the authority

Trade-off:
- a valid answer may still be missed when the model is weak; V0.2.6 reduces this risk with deterministic intents.
