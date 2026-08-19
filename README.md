# Enterprise Analytics Copilot — V0.2.7

A local-first enterprise analytics copilot that turns natural-language business questions into safe SQL and evidence-grounded analytical answers.

## What makes V0.2.7 different

This is deliberately **not** just:

```text
Question → LLM → SQL
```

The current architecture routes the problem according to its structure:

```text
                    Question
                       |
                Schema Retrieval
                       |
              Analytical Planner
                 /           \
             match          no match
               |               |
       Multi-step analysis   Intent Planner
               |             /          \
               |          known       unknown
               |            |             |
               |       Deterministic     LLM
               |          SQL            SQL
               |            \             /
               |             \           /
               +-------------- SQL Guard
                              |
                           Read-only DB
                              |
                         Evidence/Result
                              |
                         Business Answer
```

## Supported examples

### Deterministic

- `Which stores have the highest sales?`
- `Show sales by region`
- `Which stores had the highest number of orders in January?`
- `What is the average promo spend by region?`
- `What were total sales last month?`

### Analytical reasoning

- `Why did sales decline?`

For this question, V0.2.7 uses the explicit assumption:

> Compare the latest available week with the immediately preceding available week, then inspect store-level contributions.

The system measures the data rather than accepting the user's premise as fact.

## Repository structure

```text
app/
├── agent.py
├── api.py
├── config.py
├── db.py
├── main.py
├── schema.py
└── services/
    ├── analytical_planner.py
    ├── cache.py
    ├── intent_planner.py
    ├── llm.py
    ├── providers.py
    ├── schema_catalog.py
    └── sql_guard.py

docs/
├── EVOLUTION.md
├── ARCHITECTURE_DECISIONS.md
├── HLD.md
├── LLD.md
├── EVALUATION.md
├── INTERVIEW_STORY.md
├── TROUBLESHOOTING.md
├── API_EXAMPLES.md
└── decisions/

scripts/
├── init_db.py
├── demo.py
└── evaluate.py

ui/
└── streamlit_app.py

tests/
```

## Local setup

### 1. Create/activate virtual environment

Windows CMD:

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bat
python -m pip install -r requirements.txt
```

### 3. Configure environment

Copy:

```text
.env.example → .env
```

For Ollama:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:1b
```

For deterministic tests, `.env` does not matter; pytest forces the Mock provider.

### 4. Initialize the database

Always run from the repository root:

```bat
python -m scripts.init_db
```

Expected:

```text
Loaded 16 rows into data/analytics.db
```

### 5. Run tests

```bat
python -m pytest -q
```

### 6. Start API

```bat
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### 7. Start UI

In another terminal:

```bat
streamlit run ui/streamlit_app.py
```

## CLI demo

```bat
python scripts/demo.py
```

## Evaluation

```bat
python scripts/evaluate.py
```

The result is written to:

```text
artifacts/evaluation.json
```

## API

### Health

```text
GET /api/health
```

### Query

```json
POST /api/query
{
  "question": "Why did sales decline?",
  "include_sql": true
}
```

The response contains:

- business answer
- generated SQL when applicable
- result rows
- validation status
- latency/tokens/cost
- planner/analysis usage
- agent trace
- retrieved schema
- analytical steps/results when applicable

## Model strategy

The included `llama3.2:1b` configuration is a **baseline**, not a claim that 1B is the best model for NL2SQL.

V0.2.7 intentionally reduces the amount of work delegated to the model. A stronger model should be selected only after benchmarking the same workload on:

- correctness
- latency
- repair attempts
- token usage
- cost
- local resource requirements

## Engineering evolution

Read these in order:

1. `docs/EVOLUTION.md` — what failed and why the architecture changed
2. `docs/decisions/` — individual architectural decisions
3. `docs/HLD.md` — current high-level architecture
4. `docs/LLD.md` — implementation design
5. `docs/EVALUATION.md` — how the system is measured
6. `docs/INTERVIEW_STORY.md` — concise explanation for interviews

## Security note

This is a portfolio/reference implementation, not a production security certification. SQL is parsed, constrained to read-only operations and checked against the demo schema before execution. Production deployment still requires authentication, authorization, tenant isolation, secrets management, database permissions and operational controls.

## V0.2.8 — Analytical CTE validation fix

The analytical reasoning path uses trusted, code-owned multi-step CTE queries.
V0.2.8 fixes the SQL guard so CTE/derived-query output columns are recognized in
outer query scopes while the read-only and allowed-base-table checks remain in
place.
