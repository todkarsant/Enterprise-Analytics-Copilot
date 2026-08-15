# Interview Story — V0.2

## 30-second version

I built an enterprise analytics copilot that converts natural-language business questions into safe, executable SQL. The key design choice was not to trust the LLM output directly: schema context is retrieved first, SQL is generated through a provider abstraction, SQLGlot validates the parse tree and allow-lists tables/columns, failed queries can enter a bounded repair loop, and only validated read-only SQL reaches the database. The system also records latency, token usage, estimated cost, cache hits and node-level traces.

## Why this is stronger than a basic NL2SQL demo

A basic demo stops at:

`question -> LLM -> SQL`

This implementation adds:

`question -> schema context -> LLM -> validation -> bounded repair -> cache/DB -> grounded answer -> observability`

## Key trade-off

I deliberately started schema retrieval as deterministic lexical retrieval. It is cheap, reproducible and easy to test. I would move to hybrid/embedding retrieval when the schema catalog becomes large enough that lexical retrieval loses recall.

## How I would discuss hallucination

I do not treat prompt instructions as the primary hallucination control. The stronger boundary is structural: generated SQL must parse, use an allowed table/column set and be a single read-only SELECT before execution. The final answer is generated only from the returned rows.

## What I would improve next

1. Reference-result semantic evaluation.
2. Hybrid schema retrieval.
3. Redis distributed cache.
4. PostgreSQL/warehouse adapters.
5. Query timeout/cost governance.
6. Authentication and row-level authorization.
7. Production tracing and dashboards.
