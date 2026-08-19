# ADR-001 — LLM Provider Abstraction

## Context

The application needs to run locally without credentials while retaining a path to enterprise cloud inference.

## Decision

Expose a provider contract with Mock, Ollama and Azure OpenAI implementations.

## Consequences

Positive:
- local development without API keys
- deterministic tests
- model/vendor changes do not require orchestration changes

Trade-off:
- providers must normalize usage metadata and structured output behaviour.
