# Evaluation Plan — V0.2.7

The objective is to evaluate the system as an analytics product, not just whether an LLM can generate SQL.

## A. Intent Routing Accuracy

For benchmark questions with known intents:

`correctly routed intent / benchmark questions`

This is especially important after introducing deterministic planners.

## B. SQL Validity

`valid SQL / generated SQL`

For deterministic paths, the generated SQL should be stable and repeatable.

## C. Schema Contract Accuracy

A case passes when all expected result columns are present.

This is a lightweight contract test, not a full semantic correctness metric.

## D. Analytical Result Correctness

For analytical plans, compare calculated values against trusted reference calculations.

V0.2.7's `Why did sales decline?` benchmark checks:

- an analytical plan was selected
- no repair was required
- the comparison result is internally consistent
- the answer does not claim a decline when the measured change is positive

## E. Execution Success

`successful DB executions / attempted executions`

Track parser, policy and database failures separately.

## F. Hallucinated Schema Rate

`queries referencing unknown tables/columns / total generated queries`

Target should trend toward zero.

## G. Latency

Track:

- total latency
- schema retrieval
- planner latency
- SQL generation latency
- validation latency
- DB execution latency
- answer latency

Use P50/P95 once repeated benchmark runs are available.

## H. LLM Cost

When usage metadata is available:

`input_tokens / 1000 * input_price + output_tokens / 1000 * output_price`

No model price is hard-coded.

## I. Planner Value

Compare:

```text
V0.2.5/LLM-first
vs
V0.2.6/V0.2.7 hybrid routing
```

Metrics:

- LLM SQL calls avoided
- repair attempts avoided
- latency reduction
- token reduction
- correctness/regression rate

## J. Model Benchmark — next release

Keep `llama3.2:1b` as the baseline. Compare stronger models on the same benchmark before changing the default model.
