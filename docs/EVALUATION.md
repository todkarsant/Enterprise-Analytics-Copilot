# Evaluation Plan — V0.2

The objective is to evaluate the system as an analytics product, not just whether an LLM can generate SQL.

## A. SQL Validity

**Metric:** validation pass rate

`valid generated SQL / total generated SQL`

This measures whether the guardrail accepts the generated query.

## B. Schema Contract Accuracy

For each benchmark case, define expected result columns. A case passes when all required columns are present.

This is a lightweight local proxy for SQL correctness and should not be confused with full semantic accuracy.

## C. Execution Success Rate

`successful DB executions / generated SQL attempts`

Track parser failures and database failures separately.

## D. Semantic Correctness — V0.3 target

For a mature benchmark, compare the generated query result against a trusted reference query/result. Prefer result equivalence over string equality because multiple SQL statements can be semantically identical.

## E. Hallucinated Schema Rate

`queries referencing unknown tables/columns / total generated queries`

Target should trend toward zero.

## F. Latency

Track:
- total latency
- schema retrieval latency
- SQL generation latency
- validation latency
- DB execution latency
- answer generation latency

Use P50/P95 once the benchmark contains enough repeated runs.

## G. Cost

When provider token usage is available:

`estimated_cost = input_tokens / 1000 * input_price + output_tokens / 1000 * output_price`

Prices are intentionally configuration-driven; no model price is hard-coded because pricing changes.

## H. Cache Effectiveness

Track:

`cache_hit_rate = cache_hits / eligible_queries`

Compare latency for cache hits vs misses.

## I. Regression Suite

Every change to prompts, provider configuration or validation rules should run the benchmark suite. The goal is to detect regressions in:

- SQL validity
- schema correctness
- execution success
- latency
- cost
- safety rejection
