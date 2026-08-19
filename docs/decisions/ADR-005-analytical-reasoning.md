# ADR-005 — Analytical Reasoning Planner

## Context

Questions such as "Why did sales decline?" require comparison semantics and potentially multiple analytical operations. Treating them as one unconstrained NL2SQL generation step caused repeated failures with a small local model.

## Decision

Introduce a deterministic analytical planner for supported diagnostic intents. The planner defines an explicit comparison assumption, executes multiple safe analytical queries, and produces an evidence-grounded answer.

## Consequences

Positive:
- avoids fabricated causal explanations
- makes analytical assumptions visible
- supports multi-step analysis
- does not require an LLM for the current supported diagnostic intent

Trade-off:
- current analytical intent coverage is intentionally narrow
- true causal inference is outside the scope of this demo
