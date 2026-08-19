# Interview Story — V0.2.7

## 30-second version

I built an enterprise analytics copilot that converts natural-language business questions into safe analytics operations. I started with an LLM-first NL2SQL pipeline, then used observed failures to evolve it into a hybrid architecture. High-confidence intents use deterministic SQL, supported diagnostic questions use a multi-step analytical planner, and genuinely open-ended questions can fall back to an LLM. Every SQL operation passes through AST parsing and schema allow-list checks before read-only execution. The system records latency, tokens, cost, cache hits, planner usage, repair attempts and node-level traces.

## Strongest engineering point

I did not solve every problem by switching to a larger model. When the 1B model generated unnecessary SQL complexity, I constrained the problem instead. The model is now used where ambiguity actually requires generation.

## Example: "Why did sales decline?"

The system does not blindly accept the premise. It explicitly compares the latest available week with the previous available week and then checks store-level contributions. If the measured data shows growth instead of decline, the answer says so.

## Security

Prompt instructions are not treated as the security boundary. SQLGlot parsing, read-only policy, and schema allow-lists are the execution boundary.

## Trade-offs

- Deterministic planners improve reproducibility and latency but require conservative coverage.
- LLM fallback supports broader language but has higher latency and failure variability.
- A small local model is useful for a zero-key baseline but is not assumed to be the best final model.

## Next improvements

1. reference-result semantic evaluation
2. stronger-model benchmark
3. hybrid schema retrieval
4. distributed cache
5. warehouse adapter
6. authorization and row-level security
7. production tracing
