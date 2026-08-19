# Engineering Evolution — Enterprise Analytics Copilot

This document records **why the architecture changed**, not just what files changed.
The goal is to make the repository explainable during code review and interviews.

## V0.1 — Basic NL2SQL baseline

Initial mental model:

```text
Business question → LLM → SQL → database → answer
```

### Problem discovered

The LLM was implicitly trusted to produce safe and correct SQL. There was no strong security boundary, bounded recovery, or useful observability.

---

## V0.2 — Production-oriented foundation

Added:

- business-aware schema retrieval
- provider abstraction (`mock`, `ollama`, `azure_openai`)
- SQLGlot AST validation
- read-only database execution
- bounded repair loop
- TTL result cache
- node-level trace
- latency/token/cost metrics
- deterministic tests

The architecture became:

```text
Question
  ↓
Schema retrieval
  ↓
LLM SQL generation
  ↓
SQL validation
  ↓
bounded repair
  ↓
read-only execution
  ↓
answer generation
```

---

## V0.2.1 — First local Ollama run

### Observation

The SQL generation and database execution path worked, but answer generation could fail because a small local model returned malformed JSON.

### Decision

Treat LLM summarization as an enhancement rather than a dependency for basic result usability.

Added:

- tolerant JSON extraction
- deterministic answer fallback
- empty-result handling

### Engineering lesson

A downstream LLM failure should not erase a valid database result.

---

## V0.2.2 — Test isolation

### Observation

The API test expected the deterministic Mock provider, while the developer's `.env` could select Ollama.

### Decision

Force `LLM_PROVIDER=mock` in the pytest fixture.

### Result

CI/tests became independent of local model configuration.

---

## V0.2.3 — SQL alias validation bug

### Observation

A valid query such as:

```sql
SELECT region, SUM(sales) AS total_sales
FROM store_week
GROUP BY region
ORDER BY total_sales DESC
```

was rejected because `total_sales` was mistaken for a physical database column.

### Decision

Distinguish SELECT aliases from physical schema columns.

### Lesson

Security validation must understand SQL structure; simple token matching is insufficient.

---

## V0.2.4 / V0.2.5 — Table alias and self-join validation

### Observation

The small local model generated unnecessary `T1`/`T2` self-joins for simple single-table questions. The validator then needed to distinguish:

```sql
FROM store_week AS sw
```

from:

```sql
FROM store_week AS t1
JOIN store_week AS t2 ...
```

### Failure discovered

An alias count was initially used as a proxy for self-joins, which incorrectly rejected valid aliases.

### Decision

Count physical table occurrences rather than aliases.

### Lesson

A guardrail can create false positives just as easily as it can miss unsafe input; guardrails require their own regression tests.

---

## V0.2.6 — Deterministic Intent Planner

### Observation

With `llama3.2:1b`, a simple question such as:

> Which stores have the highest sales?

could result in unnecessary joins, multiple repair attempts, and high latency.

The correct SQL is obvious from the business intent:

```sql
SELECT store_id, SUM(sales) AS total_sales
FROM store_week
GROUP BY store_id
ORDER BY total_sales DESC
LIMIT 10
```

### Decision

Do not use an LLM where deterministic business logic is sufficient.

Added a conservative Intent Planner:

```text
Question
   ↓
Intent Planner
 ┌──────────────┐
 │ known intent │ → deterministic SQL
 └──────────────┘
        │
        └── unknown → LLM SQL generation
```

### Result

High-confidence queries no longer require unconstrained LLM SQL generation.

---

## V0.2.7 — Analytical reasoning layer

### Triggering question

> Why did sales decline?

### Observation

The V0.2.6 planner correctly classified this as unknown, but the 1B model attempted to invent a complex SQL query. It entered the repair loop and eventually failed.

More importantly, the question is **not just a SQL-syntax problem**. The system must first decide what comparison defines a decline.

### Decision

Introduce a conservative Analytical Planner for comparison/diagnostic questions.

For the current weekly dataset, the explicit assumption is:

> Compare the latest available week with the immediately preceding available week, then inspect store-level contributions.

The workflow becomes:

```text
Question
   ↓
Schema retrieval
   ↓
Analytical planner
   ↓
Comparison SQL
   ↓
Contributor SQL
   ↓
Validation
   ↓
Execution
   ↓
Evidence-grounded answer
```

### Important behaviour

The system does **not** assume the user's premise is true.

For the supplied demo data, the latest week is 2026-01-26 and the previous week is 2026-01-19. The implementation calculates the actual change and reports that result.

If sales increased, the answer explicitly says that the available data does not support a decline under the chosen comparison.

### Why this matters

This prevents the model from manufacturing a causal explanation for an event that the data does not show.

---

## V0.2.7 — Documentation evolution

The repository now also contains:

- `docs/EVOLUTION.md` — chronological engineering reasoning
- `docs/decisions/` — architecture decision records
- HLD/LLD updates describing the analytical planner
- an expanded evaluation script
- regression tests for the new analytical workflow

This separates:

```text
What changed?       → CHANGELOG.md
Why did it change?  → EVOLUTION.md / ADRs
How does it work?   → HLD.md / LLD.md
How do I run it?    → README.md
How is it measured? → EVALUATION.md
```

---

## Next evolution candidates

These are intentionally not implemented as V0.2.7 requirements:

1. reference-result semantic evaluation
2. stronger model benchmarking
3. hybrid schema retrieval
4. distributed cache
5. warehouse adapters
6. query cost governance
7. row-level authorization
8. production tracing


## V0.2.9 — CTE relation alias validation regression

Observed during V0.2.8 integration testing:

```text
period_comparison → Unknown table reference: p
HTTP 422
```

Root cause: the SQL guard understood CTE names such as `periods`, but did not register an outer relation alias such as `periods p`. The validator therefore rejected valid qualified references such as `p.latest_week`.

Fix: the guard now registers both the CTE relation name and its table alias as derived relations. This keeps the physical schema allow-list strict while allowing trusted analytical CTEs to reference their own projected columns.

This is recorded as a regression because the V0.2.8 CTE support was incomplete at the relation-alias level.
