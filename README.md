# Enterprise Analytics Copilot — V0.2.1


Production-oriented local reference implementation for **NL2SQL + analytics reasoning**.

This project is designed as a portfolio-grade Applied AI system rather than a simple `question -> LLM -> SQL` demo.

## What V0.2 adds over V0.1

- Business-aware schema retrieval
- Provider abstraction: Mock / Ollama / Azure OpenAI
- SQLGlot AST validation
- Table/column allow-list enforcement
- Bounded LLM SQL-repair loop
- Read-only database execution boundary
- Query result TTL cache
- Token and estimated-cost tracking when provider usage is available
- Node-level execution trace
- Evaluation benchmark
- PostgreSQL connection path for evolution beyond SQLite
- Expanded tests and design documentation

## Architecture

```text
                         +------------------+
                         | Streamlit / REST |
                         +--------+---------+
                                  |
                                  v
                         +--------+---------+
                         |      FastAPI      |
                         +--------+---------+
                                  |
                                  v
                       +----------+-----------+
                       |    LangGraph Flow    |
                       +----------+-----------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
       Schema Retrieval      LLM Provider        Query Cache
       + Business Context   Mock/Ollama/Azure       TTL
              |                   |
              +---------+---------+
                        v
                  SQL Validation
                        |
                  valid / repair
                        |
                        v
                 Read-only DB
                        |
                        v
              Grounded Answer + Trace
```

## Core safety boundary

The model is **not** trusted to enforce database safety.

```text
LLM SQL
  |
  v
SQL parser
  |
  +-- forbidden/malformed --> reject
  |
  v
Table/column allow-list
  |
  +-- unknown -------------> reject
  |
  v
Read-only execution
```

## Local stack

- Python 3.12
- FastAPI
- LangGraph
- SQLGlot
- SQLite by default
- Optional PostgreSQL connection path
- Streamlit
- Ollama optional
- Azure OpenAI optional
- pytest
- Docker / Docker Compose

## Quick start

### 1. Create environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure

```bash
copy .env.example .env
```

or Linux/macOS:

```bash
cp .env.example .env
```

The default is:

```text
LLM_PROVIDER=mock
DB_BACKEND=sqlite
```

No API key is required for the deterministic demo.

### 4. Load sample data

```bash
python scripts/init_db.py
```

### 5. Start API

```bash
uvicorn app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/health`

### 6. Start UI

In another terminal:

```bash
streamlit run ui/streamlit_app.py
```

## Example questions

Mock mode supports deterministic examples such as:

```text
Which stores have the highest sales?
Show sales by region
What is the average promo spend by region?
Which store had the highest orders in January?
Show monthly sales
Show ads spend by region
```

For open-ended NL2SQL, switch to Ollama or Azure OpenAI.

## Ollama mode

Set:

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3
```

Start Ollama and make the selected model available locally, then run the API again.

The provider requests structured JSON and uses temperature 0 for reproducibility-oriented behaviour.

## Azure OpenAI mode

Set:

```text
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_API_VERSION=<your-supported-api-version>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
```

Do not commit `.env` or API keys.

## API

### `POST /api/query`

Request:

```json
{
  "question": "Show sales by region",
  "include_sql": true
}
```

Response includes:

- generated SQL
- validation result
- result columns/rows
- grounded answer
- latency
- provider/model
- token counts where available
- estimated cost using configured pricing
- cache hit
- repair attempts
- node-level trace
- retrieved schema items

### `GET /api/health`

Returns service, provider and database configuration.

## Evaluation

Run:

```bash
python scripts/evaluate.py
```

Output is written to:

```text
artifacts/evaluation.json
```

Current local benchmark measures:

- SQL validation pass
- expected result-column contract
- row count
- latency
- cache behaviour

This is intentionally **not** claimed to be a full semantic NL2SQL benchmark. V0.3 should add trusted reference queries/results and semantic result equivalence.

## Tests

```bash
pytest -q
```

Tests cover:

- SELECT acceptance
- mutation rejection
- unknown column rejection
- multi-statement rejection
- schema retrieval
- API health
- deterministic query execution

## Docker

Create `.env`, then:

```bash
docker compose up --build
```

API:

`http://localhost:8000`

UI:

`http://localhost:8501`

## Project structure

```text
enterprise-analytics-copilot/
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── schema.py
│   └── services/
│       ├── cache.py
│       ├── llm.py
│       ├── providers.py
│       ├── schema_catalog.py
│       └── sql_guard.py
├── data/
│   └── store_week.csv
├── docs/
│   ├── HLD.md
│   ├── LLD.md
│   ├── EVALUATION.md
│   └── INTERVIEW_STORY.md
├── scripts/
│   ├── demo.py
│   ├── evaluate.py
│   └── init_db.py
├── tests/
├── ui/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md
```

## HLD / LLD

See:

- `docs/HLD.md`
- `docs/LLD.md`
- `docs/EVALUATION.md`
- `docs/INTERVIEW_STORY.md`

## Engineering decisions

### Why a provider abstraction?

The orchestration should not depend on a specific model vendor. Mock mode gives deterministic CI; Ollama gives local LLM execution; Azure OpenAI provides an enterprise-cloud path.

### Why schema retrieval before SQL generation?

A large analytics schema creates ambiguity. Supplying only the relevant business definitions reduces unnecessary context and gives the model a narrower contract.

### Why SQLGlot?

String matching alone is insufficient for SQL validation. Parsing the statement allows structural checks before database execution.

### Why bounded repair?

An unlimited repair loop can create latency/cost runaway. V0.2 caps repair attempts through configuration.

### Why cache normalized SQL results?

Repeated analytical questions can generate the same normalized query. Caching avoids unnecessary DB work and provides a measurable latency optimization path.

## Known limitations

This is a portfolio reference implementation, not a production banking/financial analytics platform.

Current limitations:

1. SQLite is the default execution backend.
2. Schema retrieval is lexical rather than vector/hybrid.
3. The local benchmark is not a complete semantic accuracy benchmark.
4. Authentication and authorization are not implemented.
5. Query timeout governance is not yet enforced at database-driver level.
6. In-process cache is not suitable for multi-instance deployment.
7. Cost estimates depend on user-supplied pricing configuration.

These limitations are deliberate and documented because a credible engineering portfolio should distinguish implemented capabilities from future production requirements.

## V0.3 roadmap

1. Trusted reference-query benchmark + semantic result equivalence
2. Hybrid schema retrieval
3. Redis distributed cache
4. Query timeout and resource governance
5. PostgreSQL/warehouse adapters
6. Role-based and row-level authorization
7. Evaluation dashboard
8. Prompt/model regression comparison
9. SQL query-plan inspection and optimization
10. Production observability integration

## Interview positioning

The strongest interview story is not:

> "I built an NL2SQL chatbot."

It is:

> "I designed a guarded analytics execution system where the LLM is one component inside a controlled pipeline. Schema context is retrieved, SQL is structurally validated, invalid queries can be repaired within a bounded budget, only validated read-only queries execute, results are cached, and latency/token/cost metrics are captured for evaluation."

That distinction is the reason this project exists.


## Troubleshooting
See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).


## Test isolation

The test suite intentionally forces `LLM_PROVIDER=mock` so tests remain
deterministic even when your local `.env` is configured for Ollama or Azure OpenAI.

Run tests from the repository root:

```bash
python -m pytest -q
```

The runtime application can still use:

```env
LLM_PROVIDER=ollama
```

without affecting the test suite.

## V0.2.3

### SQL validation hardening

The SQL guard now distinguishes **SELECT-list aliases** from physical database
columns. For example:

```sql
SELECT store_id, SUM(sales) AS total_sales
FROM store_week
GROUP BY store_id
ORDER BY total_sales DESC
```

`total_sales` is an output alias, not a physical column. V0.2.2 incorrectly
rejected this valid query as an unknown column, which caused the API to return
HTTP 422 for the deterministic mock test.

The test suite now explicitly covers this case.
