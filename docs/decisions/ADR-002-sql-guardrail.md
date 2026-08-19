# ADR-002 — SQL AST Guardrail

## Context

Prompt instructions cannot be the primary security boundary for LLM-generated SQL.

## Decision

Parse SQL with SQLGlot and allow only read-only statements using an allow-listed schema.

## Consequences

Positive:
- blocks mutation/admin operations
- blocks unknown tables and physical columns
- provides a normalized SQL representation

Trade-off:
- the validator itself needs regression tests for aliases, CTEs and legitimate SQL constructs.
