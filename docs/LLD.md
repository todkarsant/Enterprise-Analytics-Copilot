# LLD — Enterprise Analytics Copilot V0.2.7

## 1. Module Design

```text
app/
├── api.py
├── agent.py
├── config.py
├── db.py
├── schema.py
└── services/
    ├── analytical_planner.py
    ├── cache.py
    ├── intent_planner.py
    ├── llm.py
    ├── providers.py
    ├── schema_catalog.py
    └── sql_guard.py
```

## 2. Agent State

```text
question
schema
schema_items
analysis_plan
analysis_results
analysis_used
analysis_assumption
intent
planner_used
sql
normalized_sql
validation_valid
validation_reason
repair_attempts
columns
rows
answer
input_tokens
output_tokens
model
cache_hit
trace
error
```

## 3. State Machine

```text
START
  ↓
Schema Context
  ↓
Analytical Planner
  ├───────────────┐
  │ matched       │ no match
  ↓               ↓
Analytical     Intent Planner
Execution         ├───────────────┐
  ↓               │ known         │ unknown
Answer            ↓               ↓
              Deterministic     LLM SQL
              SQL               Generation
                  \               /
                   ↓             ↓
                    SQL Guard
                       ↓
                    Execute
                       ↓
                     Answer
```

## 4. Analytical Plan Contract

```python
@dataclass(frozen=True)
class AnalysisStep:
    name: str
    sql: str
    purpose: str

@dataclass(frozen=True)
class AnalysisPlan:
    intent: str
    assumption: str
    steps: tuple[AnalysisStep, ...]
```

`plan_analytical_question(question)` returns `None` when it cannot classify a supported analytical intent.

## 5. Sales Decline Analysis

The current supported workflow has two steps:

1. `period_comparison`
   - identifies latest and previous available weeks
   - calculates total sales change and percentage change
2. `store_contributors`
   - calculates store-level changes
   - ranks the most negative contributors

The SQL is deterministic and passes through the SQL guard before execution.

## 6. Answer Strategy

### Deterministic intent

Use a deterministic table-oriented answer template. No summarization LLM call is required.

### Analytical intent

Use deterministic evidence formatting. The answer explicitly states the comparison assumption and reports whether the data supports the user's premise.

### Unknown intent

Use the configured LLM summarizer, with deterministic fallback if summarization fails.

## 7. SQL Guard Contract

```python
validate_sql(
    sql: str,
    max_length: int = 4000,
    *,
    allow_repeated_table_references: bool = False,
) -> tuple[bool, str, str | None]
```

The default is strict for LLM-generated SQL. Trusted analytical plans can opt into repeated table references while retaining parser and schema validation.

## 8. Testing Strategy

- schema retrieval unit tests
- SQL mutation/allow-list tests
- alias/CTE tests
- deterministic intent tests
- analytical planner tests
- end-to-end API test for sales decline analysis
- evaluation script covering deterministic and analytical paths
