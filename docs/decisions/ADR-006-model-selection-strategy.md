# ADR-006 — Model Selection Strategy

## Context

The local `llama3.2:1b` model demonstrated weak unconstrained NL2SQL behaviour, but V0.2.6 showed that deterministic routing can remove the model from many simple queries.

## Decision

Do not replace the model blindly. Keep the 1B model as a baseline and benchmark stronger candidates on the same evaluation set before selecting a default.

## Consequences

The portfolio can demonstrate evidence-based model selection across accuracy, latency, tokens, cost and hardware requirements rather than equating a larger model with a better system.
