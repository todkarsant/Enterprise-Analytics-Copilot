# HLD — Enterprise Analytics Copilot V0.2.7

## 1. Objective

Provide a production-oriented natural-language analytics workflow that converts business questions into safe, executable analytics operations and returns evidence-grounded business answers with traceable engineering metrics.

V0.2.7 explicitly separates:

- high-confidence deterministic analytics
- multi-step analytical reasoning
- unconstrained LLM fallback

## 2. System Context

```text
+----------------------+          +----------------------+
| Streamlit UI / API  | -------> | FastAPI Query API    |
+----------------------+          +----------+-----------+
                                             |
                                             v
                                  +----------+-----------+
                                  | LangGraph Orchestrator|
                                  +----------+-----------+
                                             |
                    +------------------------+------------------------+
                    |                        |                        |
                    v                        v                        v
             Schema Retrieval       Intent / Analytical Planner    Query Cache
                    |                        |                        |
                    |              +---------+---------+              |
                    |              |                   |              |
                    |              v                   v              |
                    |       Deterministic SQL      LLM SQL fallback   |
                    |              |                   |              |
                    +--------------+---------+---------+--------------+
                                             |
                                             v
                                      SQL AST Guard
                                             |
                                             v
                                       Read-only DB
                                             |
                                             v
                                    Result / Evidence
                                             |
                                             v
                                  Deterministic or LLM
                                      Answer Layer
                                             |
                                             v
                                      Trace + Metrics
```

## 3. Routing Strategy

### Path A — high-confidence business intent

```text
Question → Intent Planner → deterministic SQL → Guard → DB → deterministic answer
```

Examples:

- highest sales by store
- sales by region
- highest orders by store
- average promotion spend by region

### Path B — supported analytical reasoning

```text
Question → Analytical Planner
         → comparison SQL
         → contributor SQL
         → Guard + DB
         → evidence-grounded answer
```

Current example:

> Why did sales decline?

Default assumption: latest available week versus immediately preceding available week, followed by store contribution analysis.

### Path C — unknown/open-ended question

```text
Question → LLM SQL generation → Guard → bounded repair → DB → LLM/fallback answer
```

This path remains deliberately constrained and observable.

## 4. Security Boundary

The LLM is never the security mechanism.

```text
LLM / planner output
        ↓
SQLGlot parser
        ↓
read-only policy
        ↓
allow-listed tables/columns
        ↓
validated SQL
        ↓
read-only DB execution
```

Trusted deterministic analytical plans may use repeated references internally, but they still pass through the parser and schema checks.

## 5. Failure Handling

| Failure | Behaviour |
|---|---|
| Empty/invalid request | Pydantic rejects request |
| LLM unavailable | trace records error; no unsafe execution |
| Invalid SQL | execution blocked |
| Unknown table/column | execution blocked |
| Multiple statements | execution blocked |
| LLM validation failure | bounded repair |
| DB execution error | controlled error; no fabricated answer |
| Empty result | deterministic no-row response |
| Analytical premise unsupported by data | report measured result rather than agreeing with premise |

## 6. Observability

Per-query metrics include:

- total latency
- row count
- provider/model
- input/output tokens
- estimated cost
- cache hit
- repair attempts
- planner/analysis usage
- node-level trace

## 7. Scalability Path

- PostgreSQL/warehouse adapter
- Redis distributed cache
- hybrid schema retrieval
- asynchronous jobs for expensive analytics
- query timeout/cost governance
- tenant-aware authorization
- centralized tracing and dashboards

## 8. Design Principle

**Use generative AI where ambiguity requires it; use deterministic engineering where the business intent is sufficiently constrained.**
