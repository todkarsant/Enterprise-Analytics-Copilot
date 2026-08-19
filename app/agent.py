from typing import TypedDict, Literal
from time import perf_counter

from langgraph.graph import StateGraph, START, END

from app.config import get_settings
from app.db import execute_readonly
from app.services.schema_catalog import retrieve_schema
from app.services.providers import get_provider
from app.services.sql_guard import validate_sql
from app.services.intent_planner import plan_question
from app.services.analytical_planner import AnalysisPlan, plan_analytical_question
from app.services.cache import TTLCache


class AgentState(TypedDict, total=False):
    question: str
    schema: str
    sql: str
    normalized_sql: str
    validation_valid: bool
    validation_reason: str
    columns: list[str]
    rows: list[list]
    answer: str
    error: str
    repair_attempts: int
    started_at: float
    latency_ms: float
    trace: list[dict]
    input_tokens: int
    output_tokens: int
    model: str
    schema_items: list[dict]
    cache_hit: bool
    intent: str
    planner_used: bool
    analysis_plan: AnalysisPlan | None
    analysis_results: dict
    analysis_used: bool
    analysis_assumption: str


settings = get_settings()
QUERY_CACHE = TTLCache(settings.cache_ttl_seconds)


def trace(state, node, started, **details):
    state.setdefault("trace", []).append(
        {"node": node, "latency_ms": round((perf_counter() - started) * 1000, 2), **details}
    )


def schema_context(state: AgentState):
    t = perf_counter()
    retrieved = retrieve_schema(state["question"], get_settings().schema_top_k)
    trace(state, "schema_retrieval", t, items=retrieved["items"])
    return {"schema": retrieved["context"], "schema_items": retrieved["items"]}


def plan_analysis(state: AgentState):
    t = perf_counter()
    plan = plan_analytical_question(state["question"])
    trace(
        state,
        "analytical_planner",
        t,
        matched=plan is not None,
        intent=plan.intent if plan else "unknown",
        assumption=plan.assumption if plan else None,
    )
    if plan:
        return {
            "analysis_plan": plan,
            "analysis_used": True,
            "intent": plan.intent,
            "planner_used": True,
            "analysis_assumption": plan.assumption,
        }
    return {"analysis_plan": None, "analysis_used": False}


def route_after_analysis_plan(state: AgentState) -> Literal["analysis_execute", "generate_sql"]:
    if state.get("analysis_plan") is not None:
        return "analysis_execute"
    return "generate_sql"


def generate_sql(state: AgentState):
    t = perf_counter()

    if not state.get("validation_reason"):
        plan = plan_question(state["question"])
        if plan is not None:
            trace(
                state,
                "intent_planner",
                t,
                intent=plan.intent,
                deterministic=True,
                reason=plan.reason,
            )
            return {
                "sql": plan.sql,
                "error": "",
                "input_tokens": state.get("input_tokens", 0),
                "output_tokens": state.get("output_tokens", 0),
                "model": "deterministic_sql_planner",
                "intent": plan.intent,
                "planner_used": True,
            }

    provider = get_provider()
    try:
        result = provider.generate_sql(
            state["question"], state["schema"], state.get("validation_reason")
        )
        trace(
            state,
            "sql_generation",
            t,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return {
            "sql": result.text,
            "error": "",
            "input_tokens": state.get("input_tokens", 0) + result.input_tokens,
            "output_tokens": state.get("output_tokens", 0) + result.output_tokens,
            "model": result.model,
            "planner_used": False,
        }
    except Exception as exc:
        trace(state, "sql_generation", t, error=str(exc))
        return {"sql": "", "error": str(exc), "planner_used": False}


def validate_node(state: AgentState):
    t = perf_counter()
    valid, reason, normalized = validate_sql(
        state.get("sql", ""), get_settings().max_sql_length
    )
    trace(state, "sql_validation", t, valid=valid, reason=reason)
    return {
        "validation_valid": valid,
        "validation_reason": reason,
        "normalized_sql": normalized or "",
    }


def route_after_validation(state: AgentState) -> Literal["execute", "repair", END]:
    if state.get("validation_valid"):
        return "execute"
    if (
        state.get("repair_attempts", 0) < get_settings().max_repair_attempts
        and not state.get("error")
    ):
        return "repair"
    return END


def repair_sql(state: AgentState):
    return {"repair_attempts": state.get("repair_attempts", 0) + 1}


def _execute_cached(state: AgentState, sql: str):
    cached = QUERY_CACHE.get(sql)
    if cached is not None:
        columns, rows = cached
        return columns, rows, True
    columns, rows = execute_readonly(sql, get_settings().max_result_rows)
    QUERY_CACHE.set(sql, (columns, rows))
    return columns, rows, False


def execute_node(state: AgentState):
    t = perf_counter()
    try:
        columns, rows, cache_hit = _execute_cached(state, state["normalized_sql"])
        trace(state, "sql_execution", t, cache_hit=cache_hit, rows=len(rows))
        return {"columns": columns, "rows": rows, "cache_hit": cache_hit}
    except Exception as exc:
        trace(state, "sql_execution", t, error=str(exc))
        return {"error": f"SQL execution failed: {exc}"}


def analytical_execute_node(state: AgentState):
    t = perf_counter()
    plan: AnalysisPlan = state["analysis_plan"]
    results = {}
    try:
        cache_hits = 0
        for step in plan.steps:
            step_t = perf_counter()
            valid, reason, normalized = validate_sql(
                step.sql,
                get_settings().max_sql_length,
                allow_repeated_table_references=True,
            )
            trace(
                state,
                "analysis_sql_validation",
                step_t,
                step=step.name,
                valid=valid,
                reason=reason,
            )
            if not valid or not normalized:
                return {
                    "error": f"Analytical plan validation failed for {step.name}: {reason}",
                    "validation_valid": False,
                    "validation_reason": reason,
                }

            exec_t = perf_counter()
            columns, rows, cache_hit = _execute_cached(state, normalized)
            cache_hits += int(cache_hit)
            trace(
                state,
                "analysis_sql_execution",
                exec_t,
                step=step.name,
                cache_hit=cache_hit,
                rows=len(rows),
            )
            results[step.name] = {
                "purpose": step.purpose,
                "sql": normalized,
                "columns": columns,
                "rows": rows,
            }

        trace(state, "analytical_execution", t, steps=len(plan.steps), cache_hits=cache_hits)
        return {
            "analysis_results": results,
            "cache_hit": cache_hits == len(plan.steps),
            "validation_valid": True,
            "validation_reason": "Analytical plan validated and executed.",
        }
    except Exception as exc:
        trace(state, "analytical_execution", t, error=str(exc))
        return {
            "error": f"Analytical execution failed: {exc}",
            "validation_valid": False,
            "validation_reason": str(exc),
        }


def _deterministic_answer(question: str, columns: list[str], rows: list[list]) -> str:
    if not rows:
        return "No rows matched the generated query."
    if "store_id" in columns and "total_sales" in columns:
        i1, i2 = columns.index("store_id"), columns.index("total_sales")
        top = rows[:5]
        lines = [f"{r[i1]}: {r[i2]:,.2f}" for r in top]
        return "Top stores by total sales:\n" + "\n".join(lines)
    if "store_id" in columns and "total_orders" in columns:
        i1, i2 = columns.index("store_id"), columns.index("total_orders")
        return "Top stores by total orders:\n" + "\n".join(
            f"{r[i1]}: {r[i2]:,.0f}" for r in rows[:5]
        )
    if "region" in columns and "total_sales" in columns:
        i1, i2 = columns.index("region"), columns.index("total_sales")
        return "Sales by region:\n" + "\n".join(
            f"{r[i1]}: {r[i2]:,.2f}" for r in rows[:10]
        )
    if "region" in columns and "avg_promo_spend" in columns:
        i1, i2 = columns.index("region"), columns.index("avg_promo_spend")
        return "Average promotion spend by region:\n" + "\n".join(
            f"{r[i1]}: {r[i2]:,.2f}" for r in rows[:10]
        )
    if "region" in columns and "total_ads_spend" in columns:
        i1, i2 = columns.index("region"), columns.index("total_ads_spend")
        return "Advertising spend by region:\n" + "\n".join(
            f"{r[i1]}: {r[i2]:,.2f}" for r in rows[:10]
        )
    return f"The query returned {len(rows)} row(s)."


def _analysis_answer(state: AgentState) -> str:
    comparison = state.get("analysis_results", {}).get("period_comparison")
    contributors = state.get("analysis_results", {}).get("store_contributors")
    if not comparison or not comparison["rows"]:
        return "I could not determine the latest-versus-previous-week sales change from the available data."

    cols = comparison["columns"]
    row = comparison["rows"][0]
    values = dict(zip(cols, row))
    latest = values.get("latest_sales")
    previous = values.get("previous_sales")
    change = values.get("sales_change")
    pct = values.get("pct_change")
    latest_week = values.get("latest_week")
    previous_week = values.get("previous_week")

    if change is None:
        return "The available data did not contain enough information to calculate the change."

    direction = "increased" if change > 0 else "declined" if change < 0 else "was unchanged"
    answer = (
        f"Using the latest available week ({latest_week}) versus the previous available "
        f"week ({previous_week}), total sales {direction} by {abs(change):,.2f} "
        f"({abs(pct):.2f}%). Latest sales were {latest:,.2f} versus {previous:,.2f}."
    )

    if change > 0:
        answer += " The data therefore does not support a sales decline under this comparison."
    elif change < 0 and contributors and contributors["rows"]:
        ccols = contributors["columns"]
        ci = {name: ccols.index(name) for name in ccols}
        negative = [r for r in contributors["rows"] if r[ci["sales_change"]] < 0]
        if negative:
            answer += " Largest negative store-level contributors: " + "; ".join(
                f"{r[ci['store_id']]} ({r[ci['sales_change']]:,.2f})" for r in negative[:3]
            ) + "."
        else:
            answer += " No individual store showed a negative change in the contributor analysis."
    return answer


def answer_node(state: AgentState):
    t = perf_counter()
    if state.get("error"):
        return {
            "answer": state["error"],
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "model": "none",
        }

    if state.get("analysis_used"):
        answer = _analysis_answer(state)
        trace(state, "answer_generation", t, model="deterministic_analytical_answer")
        return {
            "answer": answer,
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "model": "deterministic_analytical_answer",
        }

    if not state.get("rows"):
        answer = "No rows matched the generated query."
        trace(state, "answer_generation", t, model="deterministic_fallback", reason="empty_result")
        return {
            "answer": answer,
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "model": "deterministic_fallback",
        }

    if state.get("planner_used"):
        answer = _deterministic_answer(state["question"], state["columns"], state["rows"])
        trace(state, "answer_generation", t, model="deterministic_answer_template")
        return {
            "answer": answer,
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "model": "deterministic_answer_template",
        }

    provider = get_provider()
    try:
        result = provider.summarize(state["question"], state["columns"], state["rows"])
        trace(
            state,
            "answer_generation",
            t,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return {
            "answer": result.text,
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "input_tokens": state.get("input_tokens", 0) + result.input_tokens,
            "output_tokens": state.get("output_tokens", 0) + result.output_tokens,
            "model": result.model,
        }
    except Exception as exc:
        fallback = _deterministic_answer(state["question"], state["columns"], state["rows"])
        trace(state, "answer_generation", t, model="deterministic_fallback", error=str(exc))
        return {
            "answer": fallback,
            "latency_ms": round((perf_counter() - state["started_at"]) * 1000, 2),
            "model": "deterministic_fallback",
        }


def build_graph():
    b = StateGraph(AgentState)
    b.add_node("schema_context", schema_context)
    b.add_node("plan_analysis", plan_analysis)
    b.add_node("generate_sql", generate_sql)
    b.add_node("validate_sql", validate_node)
    b.add_node("repair_sql", repair_sql)
    b.add_node("execute", execute_node)
    b.add_node("analytical_execute", analytical_execute_node)
    b.add_node("answer", answer_node)

    b.add_edge(START, "schema_context")
    b.add_edge("schema_context", "plan_analysis")
    b.add_conditional_edges(
        "plan_analysis",
        route_after_analysis_plan,
        {"analysis_execute": "analytical_execute", "generate_sql": "generate_sql"},
    )
    b.add_edge("generate_sql", "validate_sql")
    b.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {"execute": "execute", "repair": "repair_sql", END: END},
    )
    b.add_edge("repair_sql", "generate_sql")
    b.add_edge("execute", "answer")
    b.add_edge("analytical_execute", "answer")
    b.add_edge("answer", END)
    return b.compile()


GRAPH = build_graph()


def run_agent(question: str) -> dict:
    started = perf_counter()
    result = GRAPH.invoke(
        {
            "question": question,
            "repair_attempts": 0,
            "started_at": started,
            "trace": [],
            "input_tokens": 0,
            "output_tokens": 0,
        }
    )
    input_tokens = result.get("input_tokens", 0)
    output_tokens = result.get("output_tokens", 0)
    cost = (
        (input_tokens / 1000) * get_settings().cost_per_1k_input_tokens_usd
        + (output_tokens / 1000) * get_settings().cost_per_1k_output_tokens_usd
    )
    analysis = None
    if result.get("analysis_plan"):
        plan: AnalysisPlan = result["analysis_plan"]
        analysis = {
            "intent": plan.intent,
            "assumption": plan.assumption,
            "steps": [
                {"name": s.name, "purpose": s.purpose, "sql": s.sql}
                for s in plan.steps
            ],
            "results": result.get("analysis_results", {}),
        }

    return {
        "question": question,
        "sql": result.get("normalized_sql") or result.get("sql", ""),
        "columns": result.get("columns", []),
        "rows": result.get("rows", []),
        "answer": result.get("answer", result.get("error", "No answer generated.")),
        "validation": {
            "valid": result.get("validation_valid", False),
            "reason": result.get("validation_reason", result.get("error", "No validation required.")),
            "normalized_sql": result.get("normalized_sql"),
        },
        "metrics": {
            "latency_ms": result.get("latency_ms", round((perf_counter() - started) * 1000, 2)),
            "rows_returned": len(result.get("rows", [])),
            "llm_provider": get_settings().llm_provider,
            "model": result.get("model", "unknown"),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 8),
            "cache_hit": result.get("cache_hit", False),
            "repair_attempts": result.get("repair_attempts", 0),
            "planner_used": result.get("planner_used", False),
            "intent": result.get("intent", "unknown"),
            "analysis_used": result.get("analysis_used", False),
        },
        "trace": result.get("trace", []),
        "schema_items": result.get("schema_items", []),
        "analysis": analysis,
    }
