# Changelog

## V0.2.0 — Production-oriented NL2SQL foundation

- Added business-aware schema retrieval.
- Added provider abstraction for Mock, Ollama and Azure OpenAI.
- Added bounded SQL repair loop.
- Added SQLGlot AST validation and allow-list enforcement.
- Added read-only execution boundary.
- Added TTL query-result caching.
- Added token/cost metrics where provider usage metadata exists.
- Added node-level trace.
- Added evaluation benchmark and engineering tests.
- Added Docker Compose local deployment.
- Added HLD, LLD, evaluation and interview documentation.

## V0.2.1 — Runtime hardening

- Fixed Ollama JSON parsing for fenced/extra-text responses.
- Added deterministic answer fallback so an LLM summarization failure does not break a valid SQL result.
- Avoided unnecessary summarization calls when SQL returns no rows.
- Added dataset-relative handling for "last month" in the deterministic provider.
- Strengthened the Ollama prompt around SQLite date semantics and dataset-relative time.
